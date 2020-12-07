#Written by Darcie Howley & Niamh Hennigan
#Student ID= 17321006 & 17418134
import csv
import math
import string
import random
import sys
from sys import stdout
import easygui
import pymsgbox
from easygui import *

#Darcie-start
print("Results printed to results.txt file in project folder ")
#needs to be put through pylinter
#Creates the file for results to printed too
sys.stdout = open("results.txt", "w")
#user inputs
text = "Please Select which column to use for classification"

# window title
title = "Select Column"

# default integer
d_int = 3

# lower bound
lower = 0

# upper bound
upper = 99999

# creating a integer box
output = integerbox(text, title, d_int, lower, upper)

class_column = int(output) #3
pymsgbox.alert('Please Select The Full Dataset \n \t (beer)', 'File Selector')
training_data_name = easygui.fileopenbox()

#Niamh-start
#returns all values in the column col
def get_column(rows,col):
    column_list = []
    for row in rows:
        column_list.append(row[col])
    return column_list

#determines how many of each classification is in the rows passed to the function
def class_counts(rows):
    counts = {}
    for row in rows:
        label = row[class_column]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

#checks if input is numeric
def is_numeric(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

#compare the current row with the question value being tested against - return true if greater than
def compare(row, feature_column, feature_value):
    if is_numeric(row[feature_column]):
            if float(row[feature_column]) >= float(feature_value):
                return True
            else:
                return False
        #if it is categorical, it returns true if the question column and value and input attribute are equal
    else:
        return row[feature_column] == feature_value

#create two lists true_results and false_results based on true/false (greater than/less than) from compare method
def split_data(rows, feature_column, value_to_test_against):
    true_results, false_results = [], []
    for row in rows:
         if compare(row, feature_column, value_to_test_against):
            true_results.append(row)
         else:
            false_results.append(row)
    return true_results, false_results

#calculate gini of the rows inputted
def calculate_gini(rows):
    labels = class_counts(rows)
    impurity = 1
    for l in labels:
        prob_of_l = labels[l] / float(len(rows))
        impurity -= prob_of_l**2
    return impurity

#calculate the information gain by getting the gini of left and right and taking that away from gini of system at that node
def calculate_info_gain(left_side,right_side, current_gini):
    Pi = float(len(left_side)/ (len(left_side) + len(right_side)))
    info_gain = current_gini - Pi * calculate_gini(left_side) - (1 - Pi) * calculate_gini(right_side)
    return info_gain

#iterate through attributes to find best attribute and attribute value to split data on
def find_best_split(rows):
    best_gain =0
    best_attribute = 0
    best_attribute_value = 0

    #calculates gini for the rows provided
    current_gini = calculate_gini(rows)
    no_features = len(rows[0])

    #iterates through the features in the dataset (i.e columns)
    for feature in range(no_features):
        #skip if the feature is the one we want to classify as - set at start
        if feature == class_column:
            continue
        column_vals = get_column(rows,feature)

        l = 0
        while l < len(column_vals):
            #value we want to check
            testing_feature_value = rows[l][feature]

            #split the data based on the testing_feature_value
            true, false = split_data(rows, feature, testing_feature_value)

            #calcualte gain based on current split
            gain = calculate_info_gain(true,false,current_gini)

            #if better gain acheived update
            if gain > best_gain:
                best_gain = gain
                best_attribute = feature
                best_attribute_value = rows[l][feature]
            l += 1

    return best_gain,best_attribute,best_attribute_value

#recursively find best attribute to split on until leaf nodes reached
def iterate_through_tree(rows):

    #find best split of data
    info_gain, feature_column, feature_value = find_best_split(rows)
    #if no information gain we must be at a leaf node
    if info_gain == 0:
        return Leaf(rows)

    #split the data on this best split
    true_rows, false_rows = split_data(rows, feature_column, feature_value )

    #recursively go through true branch until leaf reached
    true_branch = iterate_through_tree(true_rows)
    #then recursively go through false branch
    false_branch = iterate_through_tree(false_rows)

    return Decision_Node(feature_column, feature_value, true_branch, false_branch)

#class to define leaf node reached - contains the classifications at that leaf
class Leaf:
    def __init__(self,rows):
        self.predictions = class_counts(rows)

#class to define a decision node - contains the feature and feature value (to be able to split data again) and two child branches (true and false)
class Decision_Node:
    def __init__(self, feature, feature_value, true_branch, false_branch):
        self.feature = feature
        self.feature_value = feature_value
        self.true_branch = true_branch
        self.false_branch = false_branch

#method used to classify test data once tree is formed
def classify(row, node):
    if isinstance(node,Leaf):
        return node.predictions

    feature = node.feature
    feature_value = node.feature_value

    if compare(row,feature, feature_value):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)

depth = 0
def check_indent(depth):
    if depth == 0:
        indent = "|--"
    elif depth == 1:
        indent = "| |------"
    elif depth == 2:
        indent = "| | |--------"
    elif depth == 3:
        indent = "| | | |----------"
    elif depth == 4:
        indent = "| | | | |------------"
    else:
        indent = "| | | | | |--------------"
    return indent

#print out of tree
def print_tree(node,spacing="",equals="|--"):
    global depth
    indent=check_indent(depth)
    if isinstance(node,Leaf):
        print(indent+"--",node.predictions)
        return
    indent=check_indent(depth)
    print(indent+"Is "+attributes[node.feature]+" > "+str(node.feature_value)+" ?")
    depth+=1
    indent=check_indent(depth)
    print(indent+'> True:')
    print_tree(node.true_branch,spacing+"  ")
    indent=check_indent(depth)
    print(indent+"> False:")

    print_tree(node.false_branch,spacing+"  ")
    depth-=1

#print out of leaf
def print_leaf(counts):
    total = sum(counts.values())
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs


def read_in_file(file_name):
    training_data = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f,delimiter='\t')
        linecount = 0
        for row in reader:
            if linecount == 0:
                linecount += 1
            else:
                training_data.append(row)
                #print(row),l
                linecount += 1
    return training_data

def read_attributes(file_name):
    attributes = []
    with open(file_name) as f:
        reader = csv.reader(f,delimiter='\t')
        for row in reader:
            attributes = row
            break
    return attributes

if __name__ == "__main__":
    average_accuracy = 0
    i = 0
    pymsgbox.alert('Please Select Training Dataset \n (comparison_training)', 'File Selector')
    comparison_training_data = read_in_file(easygui.fileopenbox())
    pymsgbox.alert('Please Select Testing Dataset \n (comparison_testing)', 'File Selector')
    comparison_testing_data = read_in_file(easygui.fileopenbox())

    input_data = read_in_file(training_data_name)
    attributes = read_attributes(training_data_name)

    print("Manually divided 1/3 and 2/3 test file for Weka comparison")
    comparison_tree = iterate_through_tree(comparison_training_data)
    print_tree(comparison_tree)

    right2 =0
    wrong2 = 0
    for row in comparison_testing_data:
        # classify(row, tree) 
        print("Actual: %s. Predicted: %s"% (row[class_column],print_leaf(classify(row,comparison_tree))))
        for key, value in classify(row,comparison_tree).items():
            if row[class_column]==key:
                right2+=1
            else:
                wrong2+=1
    print('\n\nPercentage Correctly Classified')
    print(right2/(right2+wrong2)*100 )
    print('Percentage Incorrectly Classified')
    print(wrong2/(right2+wrong2)*100 )
    print("End of weka comparison set \n \n \n \n")

    print("The 10 itererations of randomly split data for average accuarcy result")
    while i < 10:
        
        

        # another way to get the random third
        random.shuffle(input_data)
        no_samples = (len(input_data))//3
        testing_third,training_two_thirds = [],[]
        testing_third = input_data[: no_samples]
        training_two_thirds = input_data[no_samples:]


        tree = iterate_through_tree(training_two_thirds)
        print_tree(tree)



        right = 0
        wrong = 0
        for row in testing_third:
            # classify(row, tree) 
            print("Actual: %s. Predicted: %s"% (row[class_column],print_leaf(classify(row,tree))))
            for key, value in classify(row,tree).items():
                if row[class_column]==key:
                    right+=1
                else:
                    wrong+=1
        print('\nPercentage Correctly Classified')
        print(right/(right+wrong)*100 )
        print('Percentage Incorrectly Classified')
        print(wrong/(right+wrong)*100 )

        i += 1
        average_accuracy += right/(right+wrong)
    print("\n\nAverage Accuracy over 10 iterations:")
    print(average_accuracy/10*100)

    #writing results to file
    sys.stdout.close()

