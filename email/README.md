Some code to download emails from gmail account and use DSPy to structure some post processing to
convert them to markdown (or some other format)

Run:

```
python cli.py download --sender "noreply@news.bloomberg.com" --subject "Money Stuff" --days 60
python cli.py convert -i ~/Documents/gmail_exports/raw_emails -o ~/Documents/Notes/MoneyStuff
```

TODO:
add evaluators
retry support
human feedback?


Manual testing:
`cat /tmp/foo/1980a25feb9f8ada.json | jq .body.text | python convert.py`

