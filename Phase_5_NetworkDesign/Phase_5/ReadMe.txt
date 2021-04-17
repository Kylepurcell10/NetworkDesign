Kyle Luong
-Phase 5
-Kyle Purcell and Edward Guenette

Environment
-Operating System used: Windows 10
-Programming language used: Python
-Version used: Python 3.9.2

Instructions
-This code was developed using Visual Studio Code. When opening the files in Visual Studio Code, they will appear in tabs along the top of the IDE. 
-First, run the “server.py” using the “run without debugging” in the “run” tab at the top of the IDE. 
-A message that the server is ready will appear in the terminal
-Then you go to the “client.py” tab and “run without debugging” again. 
-The terminal will that have packets that are sent to the server until the whole file has been transferred.
-If it was sucessful, the file sent from the server side should end up as the "Received_image.jpg".
-To see the server side, hit the drop-down menu where it says “2. Python Debug console” and go to “1. Python Debug console”.
-The client side would be “2. Python Debug console”.
-Finally, the server should acknowledge that the file has been received.
-The image received by the client should be the same as the one sent to the server.

For option 1 - no loss/error:
-Lines 85 and 87 need to be 0 on "server.py".
-Lines 115 and 117 need to be 0 on "client.py".

For option 2 - ACK bit error:
-Change lines 85 to whatever percent error you would like on "server.py".

For option 3 - Data bit error:
-Change lines 115 to whatever percent error you would like on "client.py".

For option 4 - ACK packet loss:
-Change lines 87 to whatever percent error you would like on "server.py".

For option 5 - Data packet loss:
-Change lines 117 to whatever percent error you would like on "client.py".

