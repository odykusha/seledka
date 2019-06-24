#!/bin/bash

usage="
Browsers version;
    --version, -v                     Get browser versions
    <tests>...                        List tests to run and py.test command-line options
"

if [ $# -gt 0 ]; then

    while [ "$1" != "" ]; do
        case $1 in

            -h | --help )
                                        echo "$usage"
                                        exit 0
                                        ;;
            -v | --version )
                                        echo ""
                                        echo $(google-chrome --version)
                                        echo $(chromedriver --version)
                                        echo $(firefox --version)
                                        echo $(geckodriver --version | head -n 1)
                                        echo Opera $(opera --version)
                                        echo $(operadriver --version)
                                        echo ""
                                        ;;
             --)
                                        shift; break
                                        ;;
            * )
                                        echo "Unimplemented option chosen: $1"
                                        exit 1
                                        ;;
        esac
        shift
    done


else
    echo "No options specified."
    echo "$usage" >&2
    exit 1
fi


pytest $@
