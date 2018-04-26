# steamgifts-management-tool
SteamGifts Group Management Tool (SGMT) is designed to give SteamGifts group admins tools needed to automatically manage their groups
The tool is built to run as a Service, and uses a MySql DB to store all collected data.

### Using the tool
The tool is currently deployed on a web server, and can be accessed through [here](http://18.217.222.235:8080/SGMT/)

### Current Features
The up-to-date features and their functionality can be seen on the live server, in the link above.

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
I chose to write the tool synchronously at the moment for 3 reasons:
1. It would take more time to write it to run asynchronously
2. Most of the commands are running against data saved in the DB, so there is no need for async run. The only part that can actually benefit from it, is the update-group-data part.
3. It may add a significant load to the web servers it uses.
Steam may not care about a couple of hundred concurrent requests. But for SteamGifts or SGTools this might be a hug of death, which will either crash their server, or get your IP blocked from it.
So for now this tool's automatic nightly update will run slowly, but safely.

### Future plans
* Better UI

### TODO
* Add to Giveaways DB: MinimumLevel, Whitelist, RegionRestricted
* CheckMonthly/CheckAllGiveawaysAccordingToRules/UserCheckFirstGiveaway: Add "no minimum level" to optional params
* CheckMonthly/CheckAllGiveawaysAccordingToRules/UserCheckFirstGiveaway: Add "not region restricted" to optional params
* CheckMonthly/CheckAllGiveawaysAccordingToRules/UserCheckFirstGiveaway: Add "not whitelist" to optional params
* CheckMonthly/CheckAllGiveawaysAccordingToRules/UserCheckFirstGiveaway: Add "group only" to optional params
* Move start_time, end_time from Group->Giveaways data, to be kept under individual GAs + Add fetching from DB by Giveaway start/end time
* Fix logger to printout errors on server error
* Support giveaways with multiple copies + integrate into value calculation and summary printouts
* Check replacing UserCheckRules with lambda AWS process
* Check replacing the heaviest flow (UpdateAllGroups) with a lambda AWS process
* Add handling large data quantities: Giveaways, Users, Games (separate into smaller chunks)
* Handle TODO leftovers
* Add remarks to code