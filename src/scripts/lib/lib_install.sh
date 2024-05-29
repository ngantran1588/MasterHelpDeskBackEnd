#!/bin/bash

# Check for docker
if which docker >/dev/null 2>&1; then
  echo "{\"library\": \"docker\", \"installed\": \"true\", \"version\": \"$(docker --version | grep -oP '(?<=version )[0-9.]+')\"}"
else
  echo "{\"library\": \"docker\", \"installed\": \"false\", \"version\": \"\"}"
fi

# Check for mongodb
if which mongod >/dev/null 2>&1; then
  echo "{\"library\": \"mongodb\", \"installed\": \"true\", \"version\": \"$(mongod --version)\"}"
else
  echo "{\"library\": \"mongodb\", \"installed\": \"false\", \"version\": \"\"}"
fi

# Check for nginx
if which nginx >/dev/null 2>&1; then
  echo "{\"library\": \"nginx\", \"installed\": \"true\", \"version\": \"$(nginx -v)\"}"
else
  echo "{\"library\": \"nginx\", \"installed\": \"false\", \"version\": \"\"}"
fi

# Check for pip
if which pip >/dev/null 2>&1; then
  echo "{\"library\": \"pip\", \"installed\": \"true\", \"version\": \"$(pip --version | grep -oP '(?<=pip )[0-9.]+')\"}"
else
  echo "{\"library\": \"pip\", \"installed\": \"false\", \"version\": \"\"}"
fi

# Check for postgresql (assuming it's installed system-wide)
if which psql >/dev/null 2>&1; then
  echo "{\"library\": \"postgresql\", \"installed\": \"true\", \"version\": \"$(psql --version)\"}"
else
  echo "{\"library\": \"postgresql\", \"installed\": \"false\", \"version\": \"\"}"
fi

#!/bin/bash

# Check for python3 (preferred)
if which python3 >/dev/null 2>&1; then
  echo "{\"library\": \"python\", \"installed\": \"true\", \"version\": \"$(python3 --version | grep -oP '(?<=version )[0-9.]+')\"}"
  exit 0  # Exit after finding python3 (assuming it's preferred)
fi

# Check for python
if which python >/dev/null 2>&1; then
  echo "{\"library\": \"python\", \"installed\": \"true\", \"version\": \"$(python --version | grep -oP '(?<=version )[0-9.]+')\"}"
else
  echo "{\"library\": \"python\", \"installed\": \"false\", \"version\": \"\"}"
fi
