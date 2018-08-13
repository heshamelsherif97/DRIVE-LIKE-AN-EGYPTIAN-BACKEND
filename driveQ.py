import argparse
import base64
from datetime import datetime
import os
import shutil
import utilsQ

import socket
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.optimizers import Adam
from keras.callbacks import ModelCheckpoint
from keras.layers import Lambda, Conv2D, MaxPooling2D, Dropout, Dense, Flatten
from utilsQ import INPUT_SHAPE, batch_generator

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

import socketio
import eventlet
import eventlet.wsgi
from PIL import Image
from flask import Flask
from io import BytesIO

from keras.models import load_model

from keras.models import Sequential
from keras.layers import Dense, Flatten
from keras.optimizers import SGD
from keras.layers.convolutional import Conv2D
import random
import time
from keras.utils.vis_utils import plot_model
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

host = "localhost"
port = 4567
backlog = 5
size = 100000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

sio = socketio.Server()
app = Flask(__name__)
global model
prev_image_array = None



def s2b(s):
    """
    Converts a string to boolean value
    """
    s = s.lower()
    return s == 'true'


def train(x):

    speed_limit = 20
    #For now we make the car accelerate, turn right and turn left
    moves = 3
    #learning rate (discount rate)
    learningRate = 0.9
    #This is the exploration rate (epsilon)
    #Its better at first to let the model try everything
    epsilon = 1.0
    #We don't want our model to stop exploring so we set a minimum epsilon
    epsilon_min = 0.01
    #We also dont want our model to explore all the time therefore we want it
    #to decay
    epsilon_decay = 0.995
    #We want to store our data for replay/so our model can remember
    memory = []
    #The max amount of stuff we want to remember
    max_memory = 50000
    model = Sequential()
    # model.add(Lambda(lambda x: x/127.5-1.0, input_shape=INPUT_SHAPE))
    # model.add(Conv2D(24, 5, 5, activation='elu', subsample=(2, 2)))
    # model.add(Conv2D(36, 5, 5, activation='elu', subsample=(2, 2)))
    # model.add(Conv2D(48, 5, 5, activation='elu', subsample=(2, 2)))
    # model.add(Conv2D(64, 3, 3, activation='elu'))
    # model.add(Conv2D(64, 3, 3, activation='elu'))
    # model.add(Dropout(0.5))
    # model.add(Flatten())
    # model.add(Dense(100, activation='elu'))
    # model.add(Dense(50, activation='elu'))
    # model.add(Dense(10, activation='elu'))
    model.add(Conv2D(32, 8, 8, activation='relu', subsample=(4,4), input_shape=(84, 84, 4)))
    model.add(Conv2D(64, 4, 4, activation='relu', subsample=(2,2)))
    model.add(Conv2D(64, 3, 3, activation='relu', subsample=(1,1)))
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(moves, activation='linear'))
    model.compile(loss='mean_squared_error', optimizer=Adam(lr=1e-6), metrics=['accuracy'])
    model.summary()
    #plot_model(model, to_file='model.png', show_shapes=True)

    if(os.path.isfile("modelQnewConv.h5")):
        model = load_model("modelQnewConv.h5")

    print("Waiting For Connection with Simulator")
    client,address = s.accept()
    print("Simulator connected")
    i = 0
    #loop over the number of epochs (essentially the number of games)
    while True:
        #We set the game_over to false as the game is just starting
        game_over = False
        #Getting first Image
        client.send("Send\n".encode('utf-8'))
        imageee = str(client.recv(200000),"utf-8").rstrip('\r\n')
        input_img1 = Image.open(BytesIO(base64.b64decode(imageee)))
        #Getting Second Image
        client.send("Send\n".encode('utf-8'))
        imageee = str(client.recv(200000),"utf-8").rstrip('\r\n')
        input_img2 = Image.open(BytesIO(base64.b64decode(imageee)))

        #Getting Third Image
        client.send("Send\n".encode('utf-8'))
        imageee = str(client.recv(200000),"utf-8").rstrip('\r\n')
        input_img3 = Image.open(BytesIO(base64.b64decode(imageee)))

        #Getting fourth Image
        client.send("Send\n".encode('utf-8'))
        imageee = str(client.recv(200000),"utf-8").rstrip('\r\n')
        input_img4 = Image.open(BytesIO(base64.b64decode(imageee)))

                # save frame
        if args.image_folder != '':
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename1 = os.path.join(args.image_folder, timestamp)
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename2 = os.path.join(args.image_folder, timestamp)
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename3 = os.path.join(args.image_folder, timestamp)
            timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
            image_filename4 = os.path.join(args.image_folder, timestamp)
            input_img1.save('{}.jpg'.format(image_filename1))
            input_img2.save('{}.jpg'.format(image_filename2))
            input_img3.save('{}.jpg'.format(image_filename3))
            input_img4.save('{}.jpg'.format(image_filename4))

        try:
            input_img1 = np.asarray(input_img1)       # from PIL image to numpy array
            input_img1 = utilsQ.preprocess(input_img1) # apply the preprocessing
            input_img1 = input_img1.reshape(1, 84, 84)
            input_img2 = np.asarray(input_img2)       # from PIL image to numpy array
            input_img2 = utilsQ.preprocess(input_img2) # apply the preprocessing
            input_img2 = input_img2.reshape(1, 84, 84)
            input_img3 = np.asarray(input_img3)       # from PIL image to numpy array
            input_img3 = utilsQ.preprocess(input_img3) # apply the preprocessing
            input_img3 = input_img3.reshape(1, 84, 84)
            input_img4 = np.asarray(input_img4)       # from PIL image to numpy array
            input_img4 = utilsQ.preprocess(input_img4) # apply the preprocessing
            input_img4 = input_img4.reshape(1, 84, 84)

        except Exception as e:
            print(e)

        input_img = np.stack((input_img1, input_img2, input_img3, input_img4), axis = 3)
        #We set the errors to false to begin with
        errors = False
        #We set the reward to 0
        reward = 0
        treward = 0
        #While the game is not over we loop
        while game_over==False:
            #Np.random.rand() returns a number between 0 and 1
            #We check if its smaller that our exploration factor
            if np.random.rand() <= epsilon and x == True:
                #if the random number is smaller than our exploration factor
                #We select a random action from our 3 actions
                action = np.random.randint(0, moves, size=1)[0]
                print("Random Action Done : "+ str(action))
            else:
                #If it's not smaller than we predict an output by inputting our
                #4 stacked images
                #ouput is the probability of our 3 directions
                output = model.predict(input_img)
                #action is the index of the highest probability and therefore
                #indicates which turn to take
                action = np.argmax(output[0])
                print("Predicted Action Done : "+ str(action))

            client.send("Action".encode('utf-8') + str(action).encode('utf-8')+"\n".encode('utf-8'))
            response2 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            #Once we've performed our action we get the next frame
            #We also check weather to reward the algorithm or not
            client.send("Send\n".encode('utf-8'))
            response3 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            input_next_img1 = Image.open(BytesIO(base64.b64decode(response3)))

            client.send("Send\n".encode('utf-8'))
            response3 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            input_next_img2 = Image.open(BytesIO(base64.b64decode(response3)))

            client.send("Send\n".encode('utf-8'))
            response3 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            input_next_img3 = Image.open(BytesIO(base64.b64decode(response3)))

            client.send("Send\n".encode('utf-8'))
            response3 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            input_next_img4 = Image.open(BytesIO(base64.b64decode(response3)))



            client.send("crash\n".encode('utf-8'))
            response4 = str(client.recv(200000),"utf-8").rstrip('\r\n')
            errors = s2b(response4)
                    # save frame
            if args.image_folder != '':
                timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
                image_filename1 = os.path.join(args.image_folder, timestamp)
                timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
                image_filename2 = os.path.join(args.image_folder, timestamp)
                timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
                image_filename3 = os.path.join(args.image_folder, timestamp)
                timestamp = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]
                image_filename4 = os.path.join(args.image_folder, timestamp)
                input_next_img1.save('{}.jpg'.format(image_filename1))
                input_next_img2.save('{}.jpg'.format(image_filename2))
                input_next_img3.save('{}.jpg'.format(image_filename3))
                input_next_img4.save('{}.jpg'.format(image_filename4))

            try:
                input_next_img1 = np.asarray(input_next_img1)       # from PIL image to numpy array
                input_next_img1 = utilsQ.preprocess(input_next_img1) # apply the preprocessing
                input_next_img1 = input_next_img1.reshape(1, 84, 84)
                input_next_img2 = np.asarray(input_next_img2)       # from PIL image to numpy array
                input_next_img2 = utilsQ.preprocess(input_next_img2) # apply the preprocessing
                input_next_img2 = input_next_img2.reshape(1, 84, 84)
                input_next_img3 = np.asarray(input_next_img3)       # from PIL image to numpy array
                input_next_img3 = utilsQ.preprocess(input_next_img3) # apply the preprocessing
                input_next_img3 = input_next_img3.reshape(1, 84, 84)
                input_next_img4 = np.asarray(input_next_img4)       # from PIL image to numpy array
                input_next_img4 = utilsQ.preprocess(input_next_img4) # apply the preprocessing
                input_next_img4 = input_next_img4.reshape(1, 84, 84)
            except Exception as e:
                print(e)

            input_next_img = np.stack((input_next_img1, input_next_img2, input_next_img3, input_next_img4), axis = 3)


            client.send("speed\n".encode('utf-8'))
            speed = float(str(client.recv(200000),"utf-8").rstrip('\r\n'))

            #If we detect lanes and therefore no errors occur we reward the algorithm
            if errors == False:
                reward = 1

            #Else if there we detect no lanes and so there is an error we
            #say its game over
            else:
                game_over = True
                reward = -1

            treward += reward


            #Game over or not we want to keep record of the steps the algo took
            #We first check if the total memoery length is bigger than the max memory
            if len(memory) >= max_memory:
                #If more memory then needed we delete the first ever element we added
                del memory[0]
            #We append it to our memory list
            memory.append((input_img, action, reward, input_next_img, game_over))
            #Next we set our input_img to our latest data
            input_img = input_next_img
            if game_over:
                # epochs = epochs + 1
                print("New Run, Total Reward: {0}, Epoch: {1}".format(treward, i))
                i = i + 1
        #Once the game is over we want to train our algo with the data we just collected
        #We check if our memory length is bigger than our batch sizeself.
        if len(memory) > 32:
        #If so then we set the batch_size to 32
            batch_size = 32
        else:
        #Else we set our batch size to whatever is in the memory
            batch_size = len(memory)
        #We are taking a random sample of 32 so not to overfit our algo
        batch = random.sample(memory, batch_size)
        #We itereate over every memory we've stored in that memory batch of 32
        print("Learning From Previous Run")
        for input_img, action, reward, input_next_img, game_over in batch:
            #if in that memory our game was over then we set the target_reward equal to reward
            target_reward = reward
            #If our game was not over
            if game_over == False:
            #This essentially is the bellman equation
            #expected long-term reward for a given action is equal to the
            #immediate reward from the current action combined with the expected
            #reward from the best future action taken at the following state.
            #The model isn't certain that for that specific action it will get the best reward
            #It's based on probability of the action, if the probability of that action is in the
            #negatives then our future reward is going to be further decreased by our learning rate
            #This is just the model being cautious, as to not set an impossible reward target
            #If the reward is impossible then the algorithm might not converge
            #Converge as in a stable condition where it can play the game without messing up
                target_reward = reward + learningRate * \
                np.amax(model.predict(input_next_img)[0])
            #So from above we essentially know what is going to happen(input_next_img)
            #assuming the game wasn't over, the algorithm did well.
            #So we want the algorithm to perform the same, essentially we
            #persuade the algorithm to do what it did to get that reward
            #so we make the algorithm predict from the previous frame(input_img)
            #but we alter its prediction according to the action that got the highest
            #reward and...
            desired_target = model.predict(input_img)
            #we set that as the target_reward...
            desired_target[0][action] = target_reward
            #So to make the algo perform the same, we associate the input_img with the
            #target we want and we fit it
            history = model.fit(input_img, desired_target, epochs=1, verbose=0)
            print(history.history["loss"])
        #Finally we check if our exploration factor is bigger than our minimum exploration
        #if so we decrease it by the decay to reduce exploration, we do this every game
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay
        client.send("restart\n".encode('utf-8'))
        response5 = str(client.recv(200000),"utf-8").rstrip('\r\n')
        print("Saving Model")
        model.save("modelQnewConv.h5", overwrite=True)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remote Driving')
    parser.add_argument(
        'image_folder',
        type=str,
        nargs='?',
        default='',
        help='Path to image folder. This is where the images from the run will be saved.'
    )
    args = parser.parse_args()

    if args.image_folder != '':
        print("Creating image folder at {}".format(args.image_folder))
        if not os.path.exists(args.image_folder):
            os.makedirs(args.image_folder)
        else:
            shutil.rmtree(args.image_folder)
            os.makedirs(args.image_folder)
        print("RECORDING THIS RUN ...")
    else:
        print("NOT RECORDING THIS RUN ...")
    x = True
    train(x)
