Tanker
===========

A tool for managing large numbers of Digital Ocean instances.

Instances are organized into a tanker, each tanker representing a group of machines. 

usage: tanker [-h]
  {list,create,destroy,private,public,keys,drops,json,comma-public,space-public,comma-private,space-private}
  
- list - list all tanker instance names
- create - create a tanker (all keys are added by default, private networking is enabled by default)
- destroy - destroy a tanker
- private - list all private images
- public - list all public images
- keys - list all keys
- drops - list all droplets in a tanker with ips (may replace list shortly)
- json - return all droplets in a tanker as json
- comma-* - return a comma separated list of all tanker droplet ips (private or public)
- space-* - return a space separated list of all tanker droplet ips (private or public)
