#!/usr/bin/env bash
#
# Check Drupal-Dev project requirements.
#
set -e

DOCTOR_CHECK_TOOLS="${DOCTOR_CHECK_TOOLS:-1}"
DOCTOR_CHECK_PORT="${DOCTOR_CHECK_PORT:-0}"
DOCTOR_CHECK_PYGMY="${DOCTOR_CHECK_PYGMY:-1}"
DOCTOR_CHECK_CLI="${DOCTOR_CHECK_CLI:-1}"
DOCTOR_CHECK_SSH="${DOCTOR_CHECK_SSH:-0}"
DOCTOR_CHECK_WEBSERVER="${DOCTOR_CHECK_WEBSERVER:-1}"
DOCTOR_CHECK_BOOTSTRAP="${DOCTOR_CHECK_BOOTSTRAP:-1}"

APP_PORT="${APP_PORT:-80}"
CLI="${CLI:-cli}"
LAGOON_LOCALDEV_URL="${LAGOON_LOCALDEV_URL:-http://your-site.docker.amazee.io/}"
SSH_KEY_FILE="${SSH_KEY_FILE:-$HOME/.ssh/id_rsa}"
DATAROOT="${DATAROOT:-.data}"

#-------------------------------------------------------------------------------
#                    DO NOT CHANGE ANYTHING BELOW THIS LINE
#-------------------------------------------------------------------------------


#
# Main entry point.
#
main() {
  status "Checking project requirements"

  if [ "${DOCTOR_CHECK_TOOLS}" == "1" ]; then
    [ "$(command_exists docker)" == "1" ] && error "Please install Docker (https://www.docker.com/get-started)" && exit 1
    [ "$(command_exists docker-compose)" == "1" ] && error "Please install docker-compose (https://docs.docker.com/compose/install/)" && exit 1
    [ "$(command_exists composer)" == "1" ] && error "Please install Composer (https://getcomposer.org/)" && exit 1
    [ "$(command_exists pygmy)" == "1" ] && error "Please install Pygmy (https://pygmy.readthedocs.io/)" && exit 1
    [ "$(command_exists ahoy)" == "1" ] && error "Please install Ahoy (https://ahoy-cli.readthedocs.io/)" && exit 1
    success "All required tools are present"
  fi

  if [ "${DOCTOR_CHECK_PORT}" == "1" ]; then
    if ! lsof -i :3000 | grep LISTEN | grep -q om.docke; then
      error "Port 3000 is occupied by a service other than Docker. Stop this service and run 'pygmy up'"
    fi
    success "Port 3000 is available"
  fi

  if [ "${DOCTOR_CHECK_PYGMY}" == "1" ]; then
    if ! pygmy status > /dev/null 2>&1; then
      error "pygmy is not running. Run 'pygmy up' to start pygmy."
      exit 1
    fi
    success "Pygmy is running"
  fi

  # Check that the stack is running.
  if [ "${DOCTOR_CHECK_CLI}" == "1" ]; then
    if ! docker ps -q --no-trunc | grep "$(docker-compose ps -q ckan)" > /dev/null 2>&1; then
      error "CLI container is not running. Run 'ahoy up'."
      exit 1
    fi
    success "CLI container is running"
  fi

  if [ "${DOCTOR_CHECK_SSH}" == "1" ]; then
    # SSH key injection is required to access Lagoon services from within
    # containers. For example, to connect to production environment to run
    # drush script.
    # Pygmy makes this possible in the following way:
    # 1. Pygmy starts `amazeeio/ssh-agent` container with a volume `/tmp/amazeeio_ssh-agent`
    # 2. Pygmy adds a default SSH key from the host into this volume.
    # 3. `docker-compose.yml` should have volume inclusion specified for CLI container:
    #    ```
    #    volumes_from:
    #      - container:amazeeio-ssh-agent
    #    ```
    # 4. When CLI container starts, the volume is mounted and an entrypoint script
    #    adds SSH key into agent.
    #    @see https://github.com/amazeeio/lagoon/blob/master/images/php/cli/10-ssh-agent.sh
    #
    #  Running `ssh-add -L` within CLI container should show that the SSH key
    #  is correctly loaded.
    #
    # As rule of a thumb, one must restart the CLI container after restarting
    # Pygmy ONLY if SSH key was not loaded in pygmy before the stack starts.
    # No need to restart CLI container if key was added, but pygmy was
    # restarted - the volume mount will retain and the key will still be
    # available in CLI container.

    # Check that the key is injected into pygmy ssh-agent container.
    if ! pygmy status 2>&1 | grep -q "${SSH_KEY_FILE}"; then
      error "SSH key is not added to pygmy. Run 'pygmy stop && pygmy start' and then 'ahoy up -- --build'."
      exit 1
    fi

    # Check that the volume is mounted into CLI container.
    if ! docker exec -i "$(docker-compose ps -q ckan)" sh -c "grep \"^/dev\" /etc/mtab|grep -q /tmp/amazeeio_ssh-agent"; then
      error "SSH key is added to Pygmy, but the volume is not mounted into container. Make sure that your your \"docker-compose.yml\" has the following lines:"
      error "volumes_from:"
      error "  - container:amazeeio-ssh-agent"
      error "After adding these lines, run 'ahoy up -- --build'"
      exit 1
    fi

    # Check that ssh key is available in the container.
    if ! docker exec -i "$(docker-compose ps -q ckan)" bash -c "ssh-add -L | grep -q 'ssh-rsa'" ; then
      error "SSH key was not added into container. Run 'ahoy up -- --build'."
      exit 1
    fi

    success "SSH key is available within CLI container"
  fi


  if [ "${DOCTOR_CHECK_WEBSERVER}" == "1" ]; then
    host_app_port="$(docker port $(docker-compose ps -q ckan) 3000 | cut -d : -f 2)"
    if ! curl -L -s -o /dev/null -w "%{http_code}" "${LAGOON_LOCALDEV_URL}:${host_app_port}" | grep -q 200; then
      error "Web server is not accessible at ${LAGOON_LOCALDEV_URL}:${host_app_port}"
      exit 1
    fi
    success "Web server is running and accessible at ${LAGOON_LOCALDEV_URL}:${host_app_port}"
  fi

  if [ "${DOCTOR_CHECK_BOOTSTRAP}" == "1" ]; then
    host_app_port="$(docker port $(docker-compose ps -q ckan) 3000 | cut -d : -f 2)"
    if ! curl -L -s -N "${LAGOON_LOCALDEV_URL}:${host_app_port}" | grep -q -i "meta name=\"generator\" content=\"ckan"; then
      error "Website is running, but cannot be bootstrapped. Try pulling latest container images with 'ahoy pull'"
      exit 1
    fi
    success "Successfully bootstrapped website at ${LAGOON_LOCALDEV_URL}:${host_app_port}"
  fi

  status "All required checks have passed"
}

#
# Check that command exists.
#
command_exists() {
  local cmd=$1
  command -v "${cmd}" | grep -ohq "${cmd}"
  local res=$?

  # Try homebrew lookup, if brew is available.
  if command -v "brew" | grep -ohq "brew" && [ "$res" == "1" ] ; then
    brew --prefix "${cmd}" > /dev/null
    res=$?
  fi

  echo ${res}
}

#
# Status echo.
#
status() {
  cecho blue "✚ $1";
}

#
# Success echo.
#
success() {
  cecho green "  ✓ $1";
}

#
# Error echo.
#
error() {
  cecho red "  ✘ $1";
  exit 1
}

#
# Colored echo.
#
cecho() {
  local prefix="\033["
  local input_color=$1
  local message="$2"

  local color=""
  case "$input_color" in
    black  | bk) color="${prefix}0;30m";;
    red    |  r) color="${prefix}1;31m";;
    green  |  g) color="${prefix}1;32m";;
    yellow |  y) color="${prefix}1;33m";;
    blue   |  b) color="${prefix}1;34m";;
    purple |  p) color="${prefix}1;35m";;
    cyan   |  c) color="${prefix}1;36m";;
    gray   | gr) color="${prefix}0;37m";;
    *) message="$1"
  esac

  # Format message with color codes, but only if a correct color was provided.
  [ -n "$color" ] && message="${color}${message}${prefix}0m"

  echo -e "$message"
}

main "$@"
