# makeshift
  A Dating application created using Django / Python. 
# FIGMA DESIGN: 
- https://www.figma.com/file/tGEQEWT4mr4CWXcP1fHKFs/Make-Shift?type=design&node-id=0%3A1&mode=design&t=RXoRcuR8pW3Lqzgm-1
# Part 1 Use Docker compose up.
OBJ 1 :
- First page is our login and access to create account which is followed in OBJ 2
- After registering and login, You are in out static/homepage
- The 4 parts should be running JS/HTML/CSS/Image
- Each have impact on page, for JS when you click the Makeshift title and color should be changed. \
OBJ 2 :
- When in login page, click create account and input the info
- If done correctly you should be redirected to login page. If not the input feilds will clear
- Use the same username and password that you created, if either wrong the input fields will clear.
- You should be redirected to the static/homepage
- Make sure the tile is present, the username is present and log out button is presnt
- If you want to log out click log out and you should be redirected back to log in. 
# Part 2 Use Docker compose up.
OBJ 1 :
- Allowed uploading images along side posts
- Images must be submitted along side posts as another required field
- Any other file submitted other than images will result in no post being created
OBJ 2 :
- Create account and login
- Next find the "Let's Chat" button and click
- You are directed to our global chat page
- This is where we implemented our websocket connection like HW 4 LO
- Enter message or read message 
