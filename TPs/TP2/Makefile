# Compiler
CC := gcc

# Compiler flags
CFLAGS := -Wall -Wextra -Werror -g -Iinclude -pthread

SRC_DIR := src
OBJ_DIR := obj
BIN_DIR := bin
INC_DIR := hdr

# Source files
USER_SRC := user.c
SERVER_SRC := server.c
MESSAGE_SRC := msg.c

# Header files
USER_HEADER := $(INC_DIR)/user.h
SERVER_HEADER := $(INC_DIR)/server.h
MESSAGE_HEADER := $(INC_DIR)/msg.h

# Object files
USER_OBJ := $(OBJ_DIR)/user.o
SERVER_OBJ := $(OBJ_DIR)/server.o
MESSAGE_OBJ := $(OBJ_DIR)/msg.o

# Executable files
USER_BIN := $(BIN_DIR)/user
SERVER_BIN := $(BIN_DIR)/server

# Targets
.PHONY: all clean

all: $(USER_BIN) $(SERVER_BIN)

$(USER_BIN): $(USER_OBJ) $(MESSAGE_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(SERVER_BIN): $(SERVER_OBJ) $(MESSAGE_OBJ)
	@mkdir -p $(BIN_DIR)
	$(CC) $(CFLAGS) $^ -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c $(USER_HEADER) $(SERVER_HEADER) $(MESSAGE_HEADER)
	@mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -I$(INC_DIR) -c $< -o $@

clean:
	rm -f $(USER_BIN) $(SERVER_BIN) $(USER_OBJ) $(SERVER_OBJ) $(MESSAGE_OBJ)