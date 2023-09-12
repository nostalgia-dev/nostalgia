# E-Mail source

This source is fed by connecting to an e-mail account via IMAP.

It expects the following environment variables to be set:

- `IMAP_HOSTNAME` the IMAP hostname, e.g. `imap.kolabnow.com`
- `IMAP_USERNAME` which is often your mail address
- `IMAP_PASSWORD` the password you log in with

You might want to store the password in a safe like KeePassXC.
On GNU/Linux, you can write a small script to automate the task of setting
those variables for you:

```sh
export IMAP_HOSTNAME="imap.kolabnow.com"
export IMAP_USERNAME="me@kolabnow.com"
keepassxc-cli clip ~/path/to/passwords.kdbx email_entry  # Unlock KeePassXC
export IMAP_PASSWORD="$(xclip -sel clipboard -o)"
echo "Got ya" | xclip -sel clipboard
```

To download it for ingestion, run the following code (may take a while):

```py
from nostalgia.sources.email import Email

Email.download()
```

Now, add the following lines to your `~/nostalgia_data/nostalgia_entry.py`:

```py
from nostalgia.sources.email import Email

email = Email.load()
```

Now, you can start a Nostalgia Timeline and inspect your mails.
Enjoy!