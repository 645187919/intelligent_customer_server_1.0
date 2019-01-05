import aiml
import os

kernel = aiml.Kernel()

if os.path.isfile("bot_brain.brn"):
    kernel.bootstrap(brainFile = "bot_brain.brn")
else:
    #当你有很多AIML文件，这需要学很长时间。这就要靠机器人大脑文件了。
    #在机器人学习了所有的AIML文件后并可以直接把大脑存到一个文件里，这样在下次启动时就可以直接加速。
    kernel.bootstrap(learnFiles = "std-startup.xml", commands = "load aiml b")
    #当AIML温江更改后可执行该代码重新生成这个文件。
    kernel.saveBrain("bot_brain.brn")

# kernel now ready for use
while True:
    print(kernel.respond(input("Enter your message >> ")))