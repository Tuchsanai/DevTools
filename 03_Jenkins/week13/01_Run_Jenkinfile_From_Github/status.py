import os

def main():
    # Displaying status
    print("System Status:")
    print("---------------")
    print("Operating System:", os.name)
    print("\n")
    print("Environment Variables:", os.environ)
    print("\n")
    print("finished.")

if __name__ == "__main__":
    main()
