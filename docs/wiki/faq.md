# Frequently Asked Questions
This is a tentative, anticipated list of issues/questions we've noted from our correspondences with memote users.

## How do I disable .yml creation when using memote with a git repository?

The automatic step of writing a .yml can take a long time for larger models and slow down the comfortable, fluent use of version controlling a model with git. It can be disabled by removing the pre-commit hook in the model repository. Navigate to this file `.git/hooks/pre-commit` in the repository folder. Either remove the file entirely or open it to comment out the last line (line 58) containing `main()`.

## I can't seem to open index.html from the terminal on my mac.

Using command `open index.html` may not always result in the html file opening properly in a browser.

As pointed out [here](https://stackoverflow.com/questions/10006958/open-an-html-file-with-default-browser-using-bash-on-mac/10250717#10250717):
> OS X provides the `open` utility to launch applications matching a file type from the shell. However, in the case of a HTML file, that is the application registered with Launch Services for the **file type** `public.html`, which can, but need not be, your default browser, or whatever editor registers as able to edit HTML. And while the default browser is registered for the **URL protocol** `http` no matter what, there is no way to access that protocol handler to open a file with `open`.

This problem seems to exist only for Google Chrome users, and running `open -a Safari index.html` will open the memote report snapshot results without any issues.
