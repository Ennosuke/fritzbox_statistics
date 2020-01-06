# fritz.box Statistics

This provides scripts to create simple statistics based on the daily usage information a fritz.box router can send.  
The tool is split in three parts which can be used separately, though they are somewhat dependend on each other.


## Requirements

You need at least a Python 3.6 installation.

First you'll need to install two dependencies that are used throughout the code just type:

```
pip install beautifulsoup4
pip install matplotlib
```

Then download the scripts in a directory of your choice.

I recommend using a virtual environment so not to install the packages in your global space.

## Setup

Before the first run you'll need to fill the config.ini with your informations. The file is as the name suggest a simple .ini file that is parsed by the scripts to get a few configurations.

## Usage

The tool is split in three parts that are three distinct scripts.

### load_imap_emails.py

This script goes through the contents of the inbox defined in the config.ini and downloads the HTML body of all emails with the text "Nutzungs-" in their name. As of right now it only supports the German version. The HTML body is saved as `YYYY-MM-DD.html` in the `html_path` setting.

The script only downloads days that it can't find in the `html_path` and `archive_path` that way we don't download more than we need.

```
python3 load_imap_emails.py
```

### parse_mail_to_csv.py

This scripts takes all .html files in the `html_path` and parses them into a CSV file specified in the `csv_file_path` setting. The parsed mails are moved to the `archive_path` to prevent parsing the data multiple times.

```
python3 parse_mail_to_csv.py
```

### genereate_montly_statistics.py

This script uses the data in the CSV file to generate statistics for one month. The month can be specified via the `-m` or `--month` option in the format `YYYY-MM`. If no month is given as an option the current month is used.

The generated graphes are stored in the `output_path` img directory and a HTML file with more informations and the graphs embedded is created with the month in the format `YYYY-MM`.

The template for the HTML file can be cound in the directory templates. _Please be advised_ that the placeholders are surrounded by `%`. If you don't want something you can delete it.


## Notes

This was created based on a reddit post by doogie120673 on the German subreddit /r/de . I just set out to create a small hackish tool for me and possibly others to use. I did not test this script with huge datasets so it may very well be that it scales horribly. This was cobbeled together over a weekend while also doing other stuff.

If you want to improve this you are more than welcomed to do so.
