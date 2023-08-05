
<p align="center">
  <img src="https://raw.githubusercontent.com/megaboi2005/bark-it/main/images/bark-it.png" />
</p>


<p align="center">I made this because twitter sucks also birds suck dogs better so bark-it ftw </p>

## Plans

- [X] Able to post .-.
- [X] Accounts
- [ ] 2 factor authentication
- [ ] No exploits LOL
- [X] User settings
- [X] Some javascript
- [ ] ebicness

## About

I was quarantined one day so I made a crappy website and decided to rewrite it and make it open source.
The old code sucked so I thought I'd rewrite it (twice). 

If you want to see the bad aiohttp-based code then go to that branch and don't complain about the constant issues you have with it.

## Credits

- Thanks to Bigjango for taking it upon themself to rewrite all the old features and optimizing my crappy code.
- Thanks to TheShadowDragon for using his javascript skills and cool ideas.
- Thanks to SkyKrye for the best art ever.
- Thanks to Wallee for showing me how bad bark-it is and helping me show how to fix it.
- Thanks to my mods, friends, and everyone who helped with testing on this project.

## Libraries
flask
cryptocode
nltk

## How to run

Open directory and type `flask run` or `python3 app.py` and hit enter. Alternatively, if you wish to run the code in debug mode, type `flask --app app.py --debug run` (Allows you to speed up checking process instead of restarting a lot).

## How do I make a theme?

Take the original, normal.html in /templates/themes, and use it as a template.

### requirements for a theme
there are required keywords that need to be a part of every custom theme made.
every keyword has ^ on both sides to indicated that its a keyword.
| KEYWORD     | USE/FUNCTION                                                |
|-------------|------------------------------------------------------------|
| ^title^     | For the title in the browser                                |
| ^version^   | Displays the version of bark-it                            |
| ^profile^   | Displays the logged in username, those logged out are defaulted to login |
| ^pfp^       | Link of the profile picture of the logged-in user         |
| ^posts^     | MUST NEED! Used to display everything in the middle of the screen, posts, settings, and more. |

