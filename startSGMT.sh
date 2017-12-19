cd /home/ec2-user/steamgifts-management-tool
python SGMTService.py > /dev/null 2>&1 & echo $! > $1
cat $1