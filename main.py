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
        
        results = t.do_test()
        success = True
        print("Src\tDest\tTTL\tLatency")
        for ((x, y), (pair_success, log)) in results.items():
                success &= pair_success
                for (ttl, lat) in log:
                        print("%s\t%s\t%d\t%f" % (x, y, ttl, lat))
        
        print("\nTest status: %s" % ("Pass" if success else "Fail"))
        
        t.close()

if __name__ == "__main__" or __name__ == "__builtin__":
        main()
