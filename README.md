# steamgifts-management-tool
SteamGifts Group Management Tool (SGMT) is designed to give SteamGifts group admins tools needed to automatically manage their groups

### Current Features 
The tool currently implements the following features:
#### Basic Features
* Print all users in a SteamGifts group
* Print all giveaways in a SteamGifts group
* Print Steam profile ID for each user in a SteamGifts group
* Print a list of all games a user won in a SteamGifts group
* Print a list of all giveaways a user created in a SteamGifts group
#### Standard Features
* Print a list of all after-n giveaways in a SteamGifts group
    * "after-n giveaways" means that after winning N games in a group, as user is required (by group rules) to create a giveaway.
    * Requires a Steam discussion where each member writes down the after-n giveaway he created
    * Does not have additional verifications (that the giveaway is unique, that the user is not entering any giveaways while it's created, etc.)  
* Print a list of users who did not create enough after-n giveaways in a SteamGifts group
    * See above.
* Print a list of users of a SteamGifts group with a negative won/gifted ratio in SteamGifts
* Print a list of users with a negative won/gifted ratio in a SteamGifts Group
* Check if a given user complies with some/all of the following rules:
    * User doesn't have non activated games
    * User doesn't have multiple wins
    * User has positive real CV ratio
    * User has no SteamRep bans and his profile is public
    * Check user is above certain level on SteamGifts
#### Advanced Features
The following features are considered advanced, as they require you to provide a cookies of a user that is a member of the SteamGifts group in question, in order to work.
* Print for a user, all the giveaways (in a SteamGifts group) he has joined since a given date (used to check if a user joined giveaways when he was not supposed to)
* Check a user has created a giveaway (in a SteamGifts group) by some/all of the following rules (usually used for new users):
    * Giveaway that is unique to the SteamGifts group (no other groups can participate)
    * Optional: The giveaway is created within X days from when the user has joined the group
    * Optional: The giveaway has a minimum of X days to exist 
    * Optional: The giveaway game has a value of at least X
    * Optional: The giveaway game has at least X reviews on Steam
    * Optional: The giveaway game has at least X score on Steam
* Print a list of users in a SteamGifts group that did not post a unique monthly giveaway in a given month/year
    * Optional: The giveaway game has a value of at least X
    * Optional: The giveaway game has at least X reviews on Steam
    * Optional: The giveaway game has at least X score on Steam

## How to Install and Run
### Python
This tool requires [Python 2.7](https://www.python.org/downloads/)

### Installing python dependencies
Within a command prompt navigate to the steamgifts-group-management-tool folder and run the command
```
pip install -r requirements.txt
``` 

### Running the tool in CLI
Within a command prompt navigate to the steamgifts-group-management-tool folder and run the command
```
python SGMTStandalone.py -h
```
This will show you a full usage explanation

### Running the tool as Service
Within a command prompt navigate to the steamgifts-group-management-tool folder and run the command
```
python SGMTService.py
```
This will bring up the service on localhost on port 5000

#### DB Schema
GroupID = hash of Group link

GiveawayID = hash of Giveaway link
* Groups: GroupID -> (Users:{UserName, GroupSent, GroupWon}, Giveaways:{GiveawayID, StartTime, EndTime})
* Users: UserName -> {SteamId, GlobalWon, GlobalSent}
* Giveaways: GiveawayID -> {GiveawayLink, GiveawayCreator, GameName, Entries:{UserName, EntryTime, Winner}, Groups:{GroupID}}
* Games: GameName -> {GameLink, GameValue, GameScore, GameNumOfReviews}

### Why Python was chosen
I chose Python as the programming language to implement this tool, for the following reasons:
1. I have previous experience with Python
2. Python is an easy language to learn (for anyone looking to contribute to this project)
3. It's very easy and fast to write a working code in Python, there is little overhead.  
4. Python has very good implementation of HTML XPath utilization library, which is easy to use
5. Python code is lightweight and runs fast.

### Why no parallelism
I chose to write the tool synchronously at the moment for 2 reasons:
1. It would take more time to write it to run asynchronously
2. It may add a significant load to the web servers it uses.
Steam may not care about a couple of hundred concurrent requests. But for SteamGifts or SGTools this might be a hug of death, which will either crash their server, or get your IP blocked from it.
So for now this tool will run slowly, but safely.

### Future plans
* Add a DB to be able to cache the data for any given SteamGifts group, which will obsolete the need for many requests to Steam, SteamGifts, SGTools, etc.
* Deploy this tool to a server somewhere, and let anyone use it as an API.
* I'm also consideting creating a SteamGifts user for the tool, then anyone wanting to use the tool, will not need to give the tool his own cookies, but instead will need to add the tool's user to his group, and the tool will use it's own user's cookies

### TODO
* Add MySql support
* Handle TODO leftovers
* Add all remaining commands to service API
* Add index.html page with usage instructions and links to service API