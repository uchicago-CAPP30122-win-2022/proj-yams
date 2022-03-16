from urban_dev_explorer.data_processing.building_permits import get_pemits
import argparse 






# parser.add_argument('--des', action='store_true', help='Sort the libaries by name in Z to A order (default: ascending order)')

    # this format for arg means that it is False by default if nothing is entered

"""
parser = argparse.ArgumentParset(description="Test or run main?")
group = parser.add_mutually_exclusive_group()
group.add_argument("--test_geocode", action = action = "store_true")
group.add_argument("--test_merge", action = "store_true")


if args.test_geocode:
elif args.test_merge:

# no test, so just run it
else:






"""




"""
import argparse
from cdp import DataPortalCollector

def main():
    collector = DataPortalCollector()
    limit = 200 
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', action="store", type=int, help='the limit of the number of libaries to receive')
    parser.add_argument('--des', action='store_true', help='Sort the libaries by name in Z to A order (default: ascending order)')
  
    args = parser.parse_args()
    
    if args.limit: 
        limit = args.limit
    
    libraries = collector.find_libraries(limit)

    if args.des:
        libraries.sort(reverse=True, key=lambda obj: obj.name)
    else:
        libraries.sort(key=lambda obj: obj.name)

    for library in libraries:
        print(library)
        print("----")


if __name__ == '__main__':
    main() 

"""