# Momento to Evernote Script #

- By Brett Hutley <brett@hutley.net>

This is a small script I wrote when I switched from iOS to Android, in order to import all my Momento entries into an Evernote notebook as separate notes (one per day).

First I exported all my Momento entries into a zip file from within the Momento app.

Next I unzipped all the entries into a directory on my notebook computer.

Each entry was a text file with the format "YYYY.MM.DD - Day, DD MMMM YYYY.txt"

There was also a sub-directory called "Attachments" that contained photos for some of the entries.

This script will iterate through these files and create an Evernote note for each one, within the specified Notebook. Each note will be named as 'YYYY-MM-DD' (the date of the entry). If there is a saved image for this date, it will also be added to the note.

In order to use this script, firstly get an Evernote developer auth_token from https://sandbox.evernote.com/api/DeveloperToken.action and modify the "momento-to-evernote.cfg" file appropriately. You can also specify the Evernote notebook to add the diary notes to.

Next copy the config file to your home directory as a dot file:

```bash
cp momento-to-evernote.cfg ~/.momento-to-evernote.cfg
```

Invoke this script with the command line:

```bash
python momento-to-evernote.py -d <path/to/momento/files>
```

You may optionally specify a 'from date'. This is useful because if you have a lot of diary entries (like I did), then the upload may trigger Evernote's rate limits which will cause the load to fail. If this happens, simply wait for a while and restart the load from the failing file.
