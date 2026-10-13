
from lib import check_cfg, get_cfg

def main(settings):
    print("Settings loaded successfully.")
    print(settings)

if __name__ == '__main__':
    if check_cfg():
        main( get_cfg() )
    else:
        print("ERR: Missing config file.")
