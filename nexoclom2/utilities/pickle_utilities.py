import pickle


def read_pickle(filename):
    with open(filename, 'rb') as file:
        return pickle.load(file)
    

def write_pickle(filename, data):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)
