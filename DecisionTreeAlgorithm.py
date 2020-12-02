import csv
import math 
import string
import random

#needs to be put through pylinter 

#user inputs
training_data_name = 'beer.txt'
class_column = 3


training_data = []
classifications = []


#returns a set of all unique values in the column col 
def find_unique_vals_in_col(rows,col):
    # unique_set = []
    # for row in rows:
    #     if row[col] not in unique_set:
    #             unique_set.append(row[col])
    # return unique_set
    return set([row[col] for row in rows])

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

#may need new name on classify

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


#print tree needs work


#print out of tree
def print_tree(node, spacing=""):
    if isinstance(node, Leaf):
        print (spacing + "Predict", node.predictions)
        return
    
    print(spacing + str(node.feature) + spacing + attributes[node.feature] + spacing + str(node.feature_value))
    
    print(spacing +'--> True:')
    print_tree(node.true_branch, spacing + "  ")

    print (spacing + '--> False:')
    print_tree(node.false_branch, spacing + "  ")

#print leaf needs work

#print out of leaf
def print_leaf(counts):
    total = sum(counts.values()) * 1.0
    probs = {}
    for lbl in counts.keys():
        probs[lbl] = str(int(counts[lbl] / total * 100)) + "%"
    return probs
    
testing_data, training_dat = [],[]

#main needs cleaning up

if __name__ == "__main__":
    with open(training_data_name, 'r') as f:
        reader = csv.reader(f,delimiter='\t')
        linecount = 0
        for row in reader:
            if linecount == 0:
                linecount += 1
                attributes = row
                #print('Attributes\n')
                #print(attributes)
            else:
                training_data.append(row)
                linecount += 1
                #every third dataset is added to testing data
                if linecount % 3 == 0:
                    testing_data.append(row)
                else:
                    training_dat.append(row)

    # another way to get the random third
    # random.shuffle(training_data)
    # no_samples = (linecount -1)//3
    # # print(linecount)
    # # print(no_samples)
    # random_third = []
    # random_third = training_data[: no_samples]
    #print(len(random_third))



    # print(testing_data)
    # print('\n')
    # print(training_dat)
    # with open ('beer.txt', 'r') as q:
        # #first_column = [row[0] for row in csv.reader(q,delimiter='\t')]
        # for row2 in csv.reader(q,delimiter='\t'):
            # print(row2)
        #print (first_column)


    # print(training_dat)
    # print(testing_data)
  
    # print(len(training_dat))
    # print(len(testing_data))  
    #print(training_data)
    print(len(training_data))
    values = find_unique_vals_in_col(training_data,3)
    print(values)
    numbers = class_counts(training_data)
    print (numbers)
    #q= Question(1,0.25)
    # print(Question(1,3))
    example = training_data[0]
    #q1 = q.compare_question_to_input(example)
    # print(q1)

    #t,f = split_data(training_data,q)

    #infGain, q4 = find_best_split(training_data)
    #print(q4)
    #print(training_data[1])
    # print('\nTHIS IS T')
    # print(t)
    # print('\nTHIS IS F')
    # print(f)

    # print (len(t))
    # print (len(f))
    ex = [ ['43.88938053', '0.548977011', '3.186363636', 'ale', '4.289230769', '16.73', '14.974', '13.44', '63.03285714'],['38.13716814', '0.328714951', '3.753636364', 'stout', '4.138461538', '18.7', '7.799368421', '10.2', '71.17142857']]
    gini = calculate_gini(training_data)
    print(gini)

    # infog = calculate_info_gain(t,f,gini)
    # print(infog)

    # b_gain,b_question = find_best_split(training_data)
    # print(b_gain)
    # print(b_question)

    # q3, info3 = iterate_through_tree(training_data)
    # print('main loop ones')
    # print(q3)
    # print(info3)
    # print('question class first')
    #tree = iterate_through_tree(training_data)
    # print_tree(tree)
    
    # print('non question class')
    tree2 = iterate_through_tree(training_data)
    # tew = isinstance(tree2, Decision_Node2)
    # print(tew)
    print_tree(tree2)
    for row in training_data:
        # classify(row, tree) 
        # classify2(row, tree2)
        #print("Actual: %s. Predicted: %s" %
         #  (row[3], print_leaf(classify(row, tree))))
        print ("Actual: %s. Predicted: %s" %
           (row[class_column], print_leaf(classify(row, tree2))))