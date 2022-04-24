from typing import List
import random
import string
import copy

class Individual():
    def __init__(self, text: List):
        self.text = text

    def mutate(self):
        index = random.choice(range(0, len(self.text)))
        symbol = random.choice(string.ascii_lowercase + string.punctuation + " ")

        self.text[index] = symbol
    
    def __str__(self):
        return ''.join(self.text)


def count_difference(str1, str2):
    difference_count = 0
    for c1,c2 in zip(str1,str2):
        if c1 != c2:
            difference_count += 1
    return difference_count

def evolve(desired_text, children_number=30, survival_size=30, max_iterations=2000):
    random_str = ''.join(random.choices(string.ascii_lowercase, k=len(desired_text)))

    individuals = [ Individual(list(random_str)) ]

    for iteration in range(max_iterations):
        children = []
        for individ in individuals:
            for _ in range(children_number):
                child = copy.deepcopy(individ)
                child.mutate()
                children.append(child)
        individuals=children
        
        individuals.sort(key=lambda x: count_difference(desired_text, x.text))
        individuals = individuals[:survival_size]

        if (count_difference(desired_text, individuals[0].text) == 0 ):
            return iteration
  