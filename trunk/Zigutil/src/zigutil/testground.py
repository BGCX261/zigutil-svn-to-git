from sppfactory import Sppobject

def main():
    a = Sppobject()
    try:
        a.weight = 'a'
    except AssertionError:
        print 'Value needs to be int or float!'
    
if __name__ == '__main__':
    main()