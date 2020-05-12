# Troubleshooting-evaluation
Python script to compare a known-good command list to a log of troubleshooting events </br>
Input:</br>
Given a log from a cisco device(*Note The syslog format is compatible with 4.3 BSD UNIX.) containing the troubleshooting session of a user, we want to compare that to a list of commands knows to resolve the inject.</br>

Output:</br>
Prints a list of attributes related to the session and user.</br>
  `kg = Known-good file path`</br>
  `tg = Target-log file path`</br>
  `un = Username`</br>
  `Elapsed time`</br>
  `Number of commands issues by the user`</br>
  `Number of commands that were not useful to the resolution`</br>
  `Average time between useful or known-good commands`</br>
  `_efficiency_ of the session = % of user commands to known-good commands`</br>

useage:</br>
`python tseval.py -g C:\knowngoodlog.txt -t C:\targetlog.txt`</br>
  `-g Known good log file prepared by evaluators`</br>
  `-t Target log file to evaluate`</br>
  `-u user's logon`</br>
