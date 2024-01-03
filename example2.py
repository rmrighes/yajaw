import asyncio
from yajaw.core import jira


# async def main():
def main():
    responses = jira.fetch_all_projects(expand=None)

    for response in responses:
        print(response["key"])
    print(f"There is a total of {len(responses)} projects.")


# if __name__ == "__main__":
#    raise SystemExit(asyncio.run(main()))

if __name__ == "__main__":
    main()
