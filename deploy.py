import os, sys


def deploy_application():

    # Get commit message
    if len(sys.argv) == 2:
        if isinstance(sys.argv[1], str):
            message = sys.argv[1]
        else:
            print("Commit message must be a string")
            return 0
    else:
        print("Please provide the commit message as the second argument")
        return 0

    # Run tests
    print("Running tests...")
    failed_tests = os.system("py manage.py test")

    # Abort if at least one test has failed
    if failed_tests:
        print("Deployment aborted.")
        return 0

    # Creating commit
    os.system("git add --all")
    os.system("git commit -m " + message)

    # Deploy to Heroku
    print("\nDeploying to Heroku...")
    os.system("git push heroku main")

    # Deploy to GitHub
    print("\nDeploying to Github...")
    os.system("git push github main")

    print("Deployment completed")
    return 1


deploy_application()
