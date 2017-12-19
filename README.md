# steamgifts-management-tool
SteamGifts Group Management Tool (SGMT) is designed to give SteamGifts group admins tools needed to automatically manage their groups
The tool is built to run as a Service, and uses a MySql DB to store all collected data.

### Using the tool
The tool is currently deployed on a web server, and can be accessed through [here](http://18.217.222.235:8080/SGMT/)

In order for the tool to be usable for any specific group, this group needs to be added. Contact me for details.

### Current Features
The tool currently implements the following features:
* [CheckMonthly](http://18.217.222.235:8080/SGMT/CheckMonthly) - Returns a list of all users who didn\'t create a "monthyl" giveaway in a given month (according to defined rules). Response example: https://imgur.com/a/4RsM9
* [UserCheckFirstGiveaway](http://18.217.222.235:8080/SGMT/UserCheckFirstGiveaway)  - Check if users comply with first giveaway rules (according to defined rules). Response example: https://imgur.com/a/afSBB
* [UserFullGiveawaysHistory](http://18.217.222.235:8080/SGMT/UserFullGiveawaysHistory)  - For a single user, show a detailed list of all giveaways he either created or participated in (Game link, value, score, winners, etc.). Response example: https://imgur.com/a/FQaqz 
* [GroupUsersSummary](http://18.217.222.235:8080/SGMT/GroupUsersSummary)  - For a given group, return summary of all giveaways created, entered and won by members. Response example: https://imgur.com/a/WSkt1 
* [UserCheckRules](http://18.217.222.235:8080/SGMT/UserCheckRules) - Check if a user complies to group rules. Response example: https://imgur.com/a/oCL3N

## How to Install and Run
### Python
This tool requires [Python 2.7](https://www.python.org/downloads/)

### Installing python dependencies
Within a command prompt navigate to the steamgifts-group-management-tool folder and run the command
```
pip install -r requirements.txt
``` 

### Running the tool in CLI - Deprecated (use at your own risk)
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
* Giveaways: GiveawayID -> {LinkURL, Creator, Value, GameName, Entries:{UserName, EntryTime, Winner}, Groups:{GroupID}}
* Games: GameName -> {Link, Value, Score, NumOfReviews}

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
* Create a SteamGifts user for the tool, then anyone wanting to use the tool, will not need to give the tool his own cookies, but instead will need to add the tool's user to his group, and the tool will use it's own user's cookies - Opened a ticket to SteamGifts Admins. Waiting for their response...

### TODO
* Make the service auto-start when machine comes up
* Add index.html page with usage instructions and links to service API
* Add scheduler for daily(?) group refreshes
* Implement CheckAllGroupGiveaways
* Add support for (Steam) game bundles (choose the best game from the bundle)
* If new user entered a group GA - Add checking if he's on one of the other groups of the GA
* Add Whitelist data to giveaways
* Handle TODO leftovers