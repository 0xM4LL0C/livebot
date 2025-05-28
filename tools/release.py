import argparse
import os
import re
import sys
from datetime import date

import changelog
import tomlkit
from semver import Version


with open("pyproject.toml") as f:
    raw_old_version = tomlkit.parse(f.read()).unwrap()["project"]["version"]
old_version = Version.parse(raw_old_version)
version = old_version


def usage(exit_code: int = 0):
    parser.print_usage()
    sys.exit(exit_code)


def run_command(command: str):
    if os.system(command):
        print(f'\n\nКоманда "{command}" завершилась с ошибкой.')
        os.system("git switch dev")
        os.system("git reset --hard HEAD~1")
        sys.exit(1)


def print_line():
    print("\n", "-" * 50, "\n", sep="")


parser = argparse.ArgumentParser(description="Bump version and create a release.")
parser.add_argument(
    "bump_type",
    choices=["finalize", "major", "minor", "patch", "prerelease", "build"],
    help="Type of version bump",
)
parser.add_argument(
    "--prerelease",
    action="store_true",
    help="Indicate if this is a prerelease",
)
args = parser.parse_args()


if args.bump_type == "prerelease" and args.prerelease:
    print("You cannot combine the 'prerelease' parameter with the '--prerelease' flag.")
    usage(1)

prerelease = args.prerelease

match args.bump_type:
    case "finalize":
        version = version.finalize_version()
    case "major":
        version = version.bump_major()
    case "minor":
        version = version.bump_minor()
    case "patch":
        version = version.bump_patch()
    case "prerelease":
        version = version.bump_prerelease()
        prerelease = True
    case "build":
        version = version.bump_build()
    case arg:
        print(f"Unknown arg `{arg}`")
        usage()
        sys.exit(1)

if prerelease and args.bump_type != "prerelease":
    version = version.bump_prerelease()

print(f"{old_version} -> {version}")

with open("CHANGELOG.md", "r") as f:
    changes = changelog.loads(f.read())

unreleased_changes = next((c for c in changes if str(c["version"]).lower() == "unreleased"), None)

if unreleased_changes:
    print("\nИзменения для новой версии:")
    print(changelog.dumps([unreleased_changes], "").strip())
    print_line()

choice = input("Сделать релиз? [N/y] ").lower()

if choice != "y":
    sys.exit(0)

run_command("git switch dev")

with open("version", "w") as f:
    f.write(str(version))

for change in changes:
    if str(change["version"]).lower() == "unreleased":
        change["version"] = version
        change["date"] = date.today()
        changes.insert(0, {"version": "Unreleased"})
        break

with open("CHANGELOG.md", "w") as f:
    f.write(changelog.dumps(changes))

with open("CHANGELOG.md") as f:
    changes = changelog.load(f)[1]

content = changelog.dumps([changes], "").strip()
semver_regexp = r"## \[(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?] - \d{4}-\d{2}-\d{2}"


if match := re.match(semver_regexp, content):
    content = content.replace(match.group(0), "").strip()

with open("release_body.md", "w") as f:
    f.write(content)

run_command("task fix && task lint && task format")
run_command('git add . && git commit -a -m "bump version" && git push')
run_command("git switch main")

run_command(
    f'gh pr create --base main --head dev --title "Release v{version}" --body "Автоматический PR для релиза версии {version}"'
)
run_command("gh pr merge dev")
run_command(
    f"gh release create v{version} --target main --notes-file release_body.md {'-p' if prerelease else ''} --title v{version}"
)

print_line()
print("\nРелиз успешно создан и опубликован.\n")
print_line()

run_command("git switch main")
run_command("git pull")
run_command("git switch dev")
run_command("git fetch --tags")
