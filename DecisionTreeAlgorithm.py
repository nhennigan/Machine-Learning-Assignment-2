import csv
import math 
import string

training_data_name = 'beer_training.csv'
training_data = []
classifications = []
class_column = 3

#returns a set of all unique values in the column col 
def find_unique_vals_in_col(rows,col):
    return set([row[col] for row in rows])

#determines how many of each classification is in the dataset
def class_counts(rows):
    counts = {}
    for row in rows:
        label = row[class_column]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1
    return counts

def is_numeric(value):
        #print('getting to is numeric check')
        try:
            float(value)
            return True
        except ValueError:
            return False
        #return value.isdigit()
        #return isinstance(value,int) or isinstance(value,float)

class Question:
    #this class is used to create and ask the questions to split the data
    
    #init to create a question based on a column attribute value and the corresponding classification
    def __init__(self,column,value):
        self.column = column
        if is_numeric(value):
            self.value = float(value)
        else:
            self.value = value 
        testing = isinstance(self.value,str)
    
    #get correct attribute of input based on question and compare to the question we made above
    def compare_question_to_input(self, input):
        #print('got into asking question')
        test_val = input[self.column]
       

        #if it is numerical, it returns true if it is greater than the question attribute
        if is_numeric(test_val):
            #print('THE ATTRIBUTE IS NUMERIC')
            if float(test_val) >= self.value:
                #print('IT IS GREATER THAN')
                return True
            else:
                return False
        #if it is categorical, it returns true if the question and input attribute are equal
        else:
            #print('the attribute is categorical')
            return test_val == self.value
#nicer print out statement
    def __repr__(self):
        condition = "=="
        if is_numeric(self.value):
            condition = ">="
        return "Is %s %s %s" % (attributes[self.column],condition,str(self.value))

#split the data into two lists depending if the result to the question asked is true of false
def split_data(rows, question):
    true_results, false_results = [], []
    for row in rows:
        if question.compare_question_to_input(row):
            true_results.append(row)
        else:
            false_results.append(row)
    return true_results,false_results

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
    # print(len(left_side))
    # print(len(right_side))

    Pi = float(len(left_side)/ (len(left_side) + len(right_side)))
    info_gain = current_gini - Pi * calculate_gini(left_side) - (1 - Pi) * calculate_gini(right_side)
    return info_gain


def find_best_split(rows):
    best_gain = 0
    best_question = None

    #calculates gini for the rows provided
    current_gini = calculate_gini(rows)
    no_features = len(rows[0]) 
    #print(no_features)

    #iterates through the features in the dataset (i.e columns)
    for feature in range(no_features):
        #print(feature)

        #skip if the feature is the one we want to classify as - set at start
        if feature == class_column:
            #print('in continue')
            continue
        #print("out of continue")

        #get all the values in the current feature column
        values = find_unique_vals_in_col(rows,feature)

        #iterate through the column down
        for val in values:
            #set the new question as the current attribute and its value
            question = Question(feature,val)
            #go through all the rows for that attribute and check them against our question 
            true_rows, false_rows = split_data(rows, question)

            #calcualte the gain of the split 
            gain = calculate_info_gain(true_rows,false_rows,current_gini)
            if gain > best_gain:
                best_gain = gain
                best_question = question
    print(best_gain)
    print(best_question)
    return best_gain,best_question

def iterate_through_tree(rows):
    info_gain, question = find_best_split(rows)

    if info_gain == 0:
        return Leaf(rows)
    
    true_rows, false_rows = split_data(rows, question)

    print('true branch first')
    true_branch = iterate_through_tree(true_rows)

    print('false branch now')
    false_branch = iterate_through_tree(false_rows)

    return Decision_Node(question, true_branch, false_branch)


class Leaf:
    def __init__(self,rows):
        self.predictions = class_counts(rows)

class Decision_Node:
    def __init__(self, question, true_branch, false_branch):
        self.question = question
        self.true_branch = true_branch
        self.false_branch = false_branch


def classify(row, node):
    if isinstance(node,Leaf):
        return node.predictions
    
    if node.question.compare_question_to_input(row):
        return classify(row, node.true_branch)
    else:
        return classify(row, node.false_branch)

def print_tree(node, spacing=""):
    """World's most elegant tree printing function."""

    # Base case: we've reached a leaf
    if isinstance(node, Leaf):
        print (spacing + "Predict", node.predictions)
        return

    # Print the question at this node
    print (spacing + str(node.question))

    # Call this function recursively on the true branch
    print (spacing + '--> True:')
    print_tree(node.true_branch, spacing + "  ")

    # Call this function recursively on the false branch
    print (spacing + '--> False:')
    print_tree(node.false_branch, spacing + "  ")


#need to assign leafs/nodes 
#need to call find best split recusively
if __name__ == "__main__":
    with open(training_data_name, 'r') as f:
        reader = csv.reader(f)
        linecount = 0
        for row in reader:
            if linecount == 0:
                linecount += 1
                attributes = row
            else:
                training_data.append(row)
                linecount += 1
    #print(training_data)
    values = find_unique_vals_in_col(training_data,3)
    #print(values)
    # numbers = class_counts(training_data)
    # print (numbers)
    q= Question(1,0.25)
    # print(Question(1,3))
    example = training_data[0]
    q1 = q.compare_question_to_input(example)
    # print(q1)

    t,f = split_data(training_data,q)
    # print('\nTHIS IS T')
    # print(t)
    # print('\nTHIS IS F')
    # print(f)

    # print (len(t))
    # print (len(f))
    ex = [ ['43.88938053', '0.548977011', '3.186363636', 'ale', '4.289230769', '16.73', '14.974', '13.44', '63.03285714'],['38.13716814', '0.328714951', '3.753636364', 'stout', '4.138461538', '18.7', '7.799368421', '10.2', '71.17142857']]
    # gini = calculate_gini(training_data)
    # print(gini)

    # infog = calculate_info_gain(t,f,gini)
    # print(infog)

    # b_gain,b_question = find_best_split(training_data)
    # print(b_gain)
    # print(b_question)

    # q3, info3 = iterate_through_tree(training_data)
    # print('main loop ones')
    # print(q3)
    # print(info3)

    tree = iterate_through_tree(training_data)
    print_tree(tree)
    for row in training_data:
        classify(row, tree)