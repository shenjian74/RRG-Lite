# RRG-Lite

RRG-Lite is a Python CLI tool for displaying Relative Rotational graph (RRG) charts.

**Supports Python >= 3.8**

![RRG-Lite Charts](https://res.cloudinary.com/doyu4uovr/image/upload/s--iD51VT-2--/f_auto/v1731069111/RRG-Lite/rrg-lite-main_ggsdbr.png)

**Unlike traditional RRG charts,**

- Tickers are shown without tail lines or labels for a cleaner look. (See [Chart controls](#chart-controls))
- Mouse and keyboard controls enhance the user experience and aid in detailed analysis.

**By default,**

- The timeframe is weekly and 14 week average is used for calculations.
- The RS momentum is calculated by comparing the current value to its value from 52 weeks ago.
- See wiki for explanation of [RS ratio and Momentum calculations](https://github.com/BennyThadikaran/RRG-Lite/wiki/RS-ratio-and-Momentum-calculations)

## Credits

This project was inspired and made possible due to the work of [An0n1mity/RRGPy](https://github.com/An0n1mity/RRGPy).

If you liked this project, please :star2: the repos to encourage more inspirational works. :heart:

## Install

`git clone https://github.com/BennyThadikaran/RRG-Lite.git`

`pip install -r requirements.txt`

**v1.0.2 adds smooth curved tail lines.** This is an optional feature.

- If tail count is less than 3, it defaults to straight lines.

**To enable curved lines**, install `scipy`.

`pip install scipy`

![Curved tail lines](https://res.cloudinary.com/doyu4uovr/image/upload/s--x4RTqGdv--/f_auto/v1731069415/RRG-Lite/rrg-lite-curved-line_pd5int.png)

## Setup user.json

To get started, you need a folder containing OHLC data (Daily timeframe or higher) in CSV format.

See [Steps to create user.json](https://github.com/BennyThadikaran/RRG-Lite/wiki/Setup#steps-to-create-the-configuration-file)

#### Using EOD2 as data source

To use [EOD2](https://github.com/BennyThadikaran/eod2) as your data source, follow the [install instructions here](https://github.com/BennyThadikaran/eod2/wiki/Installation) to setup EOD2.

Set the `DATA_PATH` in your user.json to the full path to EOD2 daily folder located in src/eod2_data/daily.

You can download my sectors watchlist file that works with EOD2 - [sectors.csv](https://res.cloudinary.com/doyu4uovr/raw/upload/v1730526283/RRG-Lite/sectors_vwqau3.csv)

## Quick Usage

Make sure to set up your configuration file.

```bash
# assuming DATA_PATH, WATCHLIST_FILE, and BENCHMARK have been setup
py init.py
```

**Pass a benchmark index using `-b` or `--benchmark` and a list of symbol names using `--sym`.**

`py init.py -b "nifty bank" --sym csbbank rblbank indianb ucobank`

**Pass a watchlist file using `-f` or `--file` option**

`py init.py -f nifty50.csv`

**To display help use the `-h` option.**

`py init.py -h`

## Chart controls

**Left Mouse click on any point (marker)** to display/highlight the tail line and label.

**When a line is highlighted:**

- Press `Left arrow` or `Right arrow` keys to cycle through each marker on the line, diplaying a date label. (see image below)
- Press **`delete`** to remove all highlighted lines.

![date labels in rrg chart](https://res.cloudinary.com/doyu4uovr/image/upload/s--YQhUxYZK--/f_auto/v1731069111/RRG-Lite/rrg-lite-date-labels_y5ba0o.png)

Press **`h`** to toggle help text (Keybindings) in the chart.

Press **`a`** to toggle displaying ticker labels (Annotations)

Press **`t`** to toggle tail lines for all tickers.

Press **`q`** to quit the chart.

To reset the chart, press **`r`**

To use the `zoom to rectangle` tool - Press **`o`** (useful when lots of symbols on the chart.)

Matplotlib provides useful window controls like zooming and panning. Read the links below on how to use the various tools.

[Interactive navigation](https://matplotlib.org/stable/users/explain/figure/interactive.html#interactive-navigation)

[Navigation keyboard shortcuts](https://matplotlib.org/stable/users/explain/figure/interactive.html#navigation-keyboard-shortcuts)
