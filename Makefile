SERVICE = $(shell grep SERVICE MANIFEST | cut -d '=' -f2)
VERSION = $(shell grep VERSION MANIFEST | cut -d '=' -f2)




include ./image.mk

