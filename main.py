import argparse, os
from jadhoc_test import jadhoc_test

def main():
        """ Parses command line arguments, instantiate test manager, and run tests.
        """
        
        if os.geteuid() != 0:
                print("Error: you must run this script as root!")
                return
        
        parser = argparse.ArgumentParser()
        parser.add_argument('xml_file', type=str)
        args = parser.parse_args()
        t = jadhoc_test(args.xml_file)
        t.do_test()
        t.close()

if __name__ == "__main__" or __name__ == "__builtin__":
        main()
