import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from scipy import interpolate

    scipy_installed = True
except ModuleNotFoundError:
    scipy_installed = False


from loaders import AbstractLoader

version = "1.0.2"


class RRG:
    def __init__(
        self,
        config: dict,
        loader: AbstractLoader,
        watchlist: pd.DataFrame,
        tail_count=4,
        benchmark=None,
    ):
        self.watchlist = watchlist

        benchmark_config = config.get("BENCHMARK", None)

        if benchmark:
            self.benchmark = benchmark
        elif benchmark_config:
            self.benchmark = benchmark_config
        else:
            raise ValueError(
                "No benchmark index set. Use `-b` or specify `BENCHMARK` in config."
            )

        # Tail count set to minimum 2
        self.tail_count = max(2, tail_count)

        self.window = config.get("WINDOW", 14)
        self.period = config.get("PERIOD", 52)
        self.config = config

        # Keep track of data points, lines and text annotations
        self.state = {}

        # Keep track of the alpha state of lines and text
        self.text_alpha_state = 0
        self.line_alpha_state = 0

        # Default alpha values for lines and text
        self.text_alpha = 0.6
        self.line_alpha = 0.5

        self.help_plt = None

        self.help_str = """
        Keyboard Shortcuts

        delete - Remove all lines and annotations
        a         - Toggle text annotations
        t          - Toggle tail lines
        h         - Print this help text

        Mouse interaction

        Left click on Marker to toggle visibility of 
        tail, markers and labels
        """

        self.key_handler = dict(
            delete=self._clear_all,
            a=self._toggle_text,
            t=self._toggle_lines,
            h=self._toggle_help,
        )

        self.loader = loader

    def get_smooth_curve(self, x, y):
        # Interpolate a smooth curve through the scatter points
        tck, _ = interpolate.splprep([x, y], s=0)  # s=0 for no smoothing
        t = np.linspace(0, 1, 100)  # Parameter values
        line_x, line_y = interpolate.splev(t, tck)  # Evaluate spline
        return line_x, line_y

    def plot(self):
        txt_alpha = 0.4
        bg_alpha = 0.2

        colors = np.random.rand(len(self.watchlist), 3) * 0.6

        bm = self.loader.get(self.benchmark)

        if bm is None or bm.empty:
            raise ValueError(
                f"Unable to load benchmark data for {self.benchmark}"
            )

        bm = bm.loc[:, "Close"]

        # Setup the chart
        self.fig, axs = plt.subplots()
        axs.format_coord = self._format_coords

        plt.tight_layout()
        plt.xlim(93.5, 106.5)
        plt.ylim(93.5, 106.5)

        axs.set_title(
            f"RRG - {self.benchmark.upper()} - {bm.index[-1]:%d %b %Y}"
        )
        axs.set_xlabel("RS Ratio")
        axs.set_ylabel("RS Momentum")

        # Center line that divided the quadrant
        axs.axhline(y=100, color="black", linestyle="--", linewidth=0.3)
        axs.axvline(x=100, color="black", linestyle="--", linewidth=0.3)

        # Labels for each quadrant
        axs.text(94, 105.5, "Improving", fontweight="bold", alpha=txt_alpha)
        axs.text(105, 105.5, "Leading", fontweight="bold", alpha=txt_alpha)
        axs.text(105, 94, "Weakening", fontweight="bold", alpha=txt_alpha)
        axs.text(94, 94, "Lagging", fontweight="bold", alpha=txt_alpha)

        # Background colors for each quadrant
        axs.fill_between([93.5, 100], 100, 106.5, color="aqua", alpha=bg_alpha)
        axs.fill_between([100, 106.5], 100, 106.5, color="lime", alpha=bg_alpha)
        axs.fill_between(
            [100, 106.5], 93.5, 100, color="yellow", alpha=bg_alpha
        )
        axs.fill_between(
            [93.5, 100], 93.5, 100, color="orangered", alpha=bg_alpha
        )

        # Start calculation of RS and RS Momentum
        for i in self.watchlist.index:
            name, short_name = self.watchlist.loc[i, ["SYMBOL", "ABBREV"]]

            if pd.isna(short_name):
                short_name = name

            df = self.loader.get(name)

            if df is None or df.empty:
                continue

            df = df.loc[:, "Close"]

            rsr = self._calculate_rs(df, bm)

            rsm = self._calculate_momentum(rsr)

            annotation = axs.annotate(
                short_name.upper(),
                xy=(rsr.iloc[-1], rsm.iloc[-1]),
                xytext=(5, -3),
                textcoords="offset points",
                horizontalalignment="left",
                alpha=0,
            )

            # Plot the head marker (latest data point - Visible)
            marker = axs.scatter(
                x=rsr.iloc[-1],
                y=rsm.iloc[-1],
                s=40,
                color=colors[i],
                marker="o",
                picker=True,
            )

            url = f"s{i}"
            marker.set_url(url)

            # Plot the tail markers (Not visible by default)
            markers = axs.scatter(
                x=rsr.iloc[-self.tail_count : -1],
                y=rsm.iloc[-self.tail_count : -1],
                c=[colors[i]] * (self.tail_count - 1),
                s=20,
                marker="o",
                alpha=0,
            )

            if scipy_installed and self.tail_count > 3:
                x, y = self.get_smooth_curve(
                    rsr.iloc[-self.tail_count :], rsm.iloc[-self.tail_count :]
                )
            else:
                x = rsr.iloc[-self.tail_count :]
                y = rsm.iloc[-self.tail_count :]

            line = axs.plot(
                x,
                y,
                linestyle="-",
                color=colors[i],
                linewidth=1.2,
                alpha=0,
            )[0]

            self.state[url] = dict(
                line=line,
                markers=markers,
                annotation=annotation,
            )

        self.fig.canvas.mpl_connect("pick_event", self._on_pick)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)

        # Display the chart window in full screen
        window_manager = plt.get_current_fig_manager()

        if window_manager:
            if "win" in sys.platform:
                try:
                    # Only works with tkAgg backend
                    window_manager.window.state("zoomed")
                except AttributeError:
                    window_manager.full_screen_toggle()
            else:
                window_manager.full_screen_toggle()

        self.axs = axs

        plt.show()

    def _calculate_rs(
        self, stock_df: pd.Series, benchmark_df: pd.Series
    ) -> pd.Series:
        """
        Returns the RS ratio as a multiple of standard dev of SMA(RS)

        - Take the difference of RS and SMA(RS).
        - Divide the difference with the standard deviation of SMA(RS)
        - Add 100 to serve as a base value
        """
        rs = (stock_df / benchmark_df) * 100

        rs_sma = rs.rolling(window=self.window)

        return ((rs - rs_sma.mean()) / rs_sma.std(ddof=1)).dropna() + 100

    def _calculate_momentum(self, rs_ratio: pd.Series) -> pd.Series:
        """
        Returns the RS momentum as a multiple of standard deviation of SMA(ROC)

        - Calculate the ROC using the first value as base
        - Take the difference of ROC and SMA(ROC)
        - Divide the difference with the standard deviation of SMA(ROC)
        - Add 100 to serve as a base value
        """

        pos = min(len(rs_ratio), self.period)

        # Rate of change (ROC) with first value as base
        rs_roc = ((rs_ratio / rs_ratio.iloc[-pos]) - 1) * 100

        roc_sma = rs_roc.rolling(window=self.window)

        return ((rs_roc - roc_sma.mean()) / roc_sma.std(ddof=1)).dropna() + 100

    def _clear_all(self):
        """
        Clear all additional markers and text annotations
        """
        updated = False

        for url in self.state:
            line = self.state[url]["line"]

            if line._alpha:
                updated = True
                line.set_alpha(0)
                self.state[url]["markers"].set_alpha(0)
                self.state[url]["annotation"].set_alpha(self.text_alpha_state)

        if updated:
            self.fig.canvas.draw_idle()

    def _toggle_text(self):
        """
        Toggle text labels on the data points.
        """
        alpha = self.text_alpha if self.text_alpha_state == 0 else 0

        for url in self.state:
            annotation = self.state[url]["annotation"]

            # If a text is already highlighted, skip it
            if annotation._alpha == 1:
                continue

            annotation.set_alpha(alpha)

        self.text_alpha_state = alpha
        self.fig.canvas.draw_idle()

    def _toggle_lines(self):
        """
        Toggle tail line visibility
        """

        # if current state of alpha is 0, set alpha to its default value, else 0
        alpha = self.line_alpha if self.line_alpha_state == 0 else 0

        for url in self.state:
            line = self.state[url]["line"]

            # If a line is already highlighted, skip it
            if line._alpha == 1:
                continue

            line.set_alpha(alpha)

        # set the new state
        self.line_alpha_state = alpha
        self.fig.canvas.draw_idle()

    def _toggle_help(self):
        """
        Toggle Help text
        """

        if self.help_plt is None:
            self.help_plt = self.axs.text(
                100,
                100,
                self.help_str,
                color="black",
                backgroundcolor="white",
                fontweight="bold",
            )
        else:
            self.help_plt.remove()
            self.help_plt = None

        self.fig.canvas.draw_idle()

    def _format_coords(self, x, y):
        """
        A function to format the coordinate string
        """
        return f"RS: {x:.2f}     MOM: {y:.2f}"

    def _on_pick(self, event):
        """
        Handler for the pick event (when the head marker is clicked).

        Toggle visibility of line, markers and text annotations.
        """
        marker = event.artist

        url = marker.get_url()

        line = self.state[url]["line"]
        markers = self.state[url]["markers"]
        annotation = self.state[url]["annotation"]

        # toggle visibility of tail markers
        markers.set_alpha(markers._alpha == 0 or 0)

        # toggle visibility of tail lines
        if self.line_alpha_state == self.line_alpha:
            # If lines are visible, set the alpha to 1,
            # else set to default visibility.
            line.set_alpha(line._alpha == self.line_alpha or self.line_alpha)
        else:
            line.set_alpha(line._alpha == 0 or 0)

        if self.text_alpha_state == self.text_alpha:
            # If text labels are visible, set the alpha to 1,
            # else set to default visibility
            annotation.set_alpha(
                annotation._alpha == self.text_alpha or self.text_alpha
            )
        else:
            annotation.set_alpha(annotation._alpha == 0 or 0)

        self.fig.canvas.draw_idle()

    def _on_key_press(self, event):
        """
        Handler for the key press event.
        """
        key = event.key

        if key in self.key_handler:
            self.key_handler[key]()
