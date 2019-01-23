1. Checkout the develop branch and pull in the latest changes.

   ```bash
   git checkout develop
   git pull
   ```

2. Open the `HISTORY.rst` and check that everything under the heading 'Next Release' matches with what has been 
   committed since the last tagged release (`gitk`, `git log --oneline`, or PyCharm can help with looking at past 
   commits).

3. Insert a new section header with the intended version and release date above the most recent change log. 
   Everything that was under 'Next Release' should now be under that header while 'Next Release' is an empty 
   section above that.

   ```rst
   Next Release
   ------------

   1.20.4 (2019-05-01)
   -------------------
   ```

4. Commit your changes to `HISTORY.rst`.

5. Run bumpversion to update the version information in files and automatically tag the commit. When you run 
   bumpversion you have the option to increase the `major`, `minor`, or `patch` part of the version. **Please 
   follow the standards for [semantic versioning](https://semver.org/)**, e.g.,

   ```bash
   bumpversion patch
   ```

   **The major version should never be increased unless the whole team agrees.**

6. Push everything back to GitHub triggering Travis to create releases and merge the current stable state into 
   master. Say you bumped the version to `1.20.4` then your commands will be:

   ```bash
   git push origin 1.20.4  # Pushing the tag will create releases on PyPi and GitHub.
   git push origin develop
   git checkout master
   git pull  # In order to update your branch in case you forgot.
   git merge develop
   git push origin master
   ```
