#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <stdio.h>
#include <stdlib.h>

#define XOFFSET 50
#define YOFFSET 150

typedef enum {L,J,T,S,Z,I,O} tType;

//block[0][0] is anchor point for position
typedef struct tetromino {
    int blocks[4][2];
    int position[2];
    int rotation;
    tType type;
}tetromino;

typedef struct Game {
    int lineCount;
    int score;
    int grid[10][20];
    int gridColours[10][20];
}Game;

tetromino PIECES[7] = {
    {{{0,0},{0,1},{0,2},{1,2}},{4,0}},
{{{1,0},{1,1},{1,2},{0,2}},{4,0}},
{{{0,1},{1,0},{1,1},{1,2}},{4,0}},
{{{1,0},{2,0},{0,1},{1,1}},{4,0}},
{{{0,0},{1,0},{1,1},{2,1}},{4,0}},
{{{0,0},{0,1},{0,2},{0,3}},{4,0}},
{{{0,1},{1,0},{1,1},{1,2}},{4,0}}
};

int oRotations[4][4][2] = {
    {{0,0},{0,1},{1,0},{1,1}},
    {{0,0},{0,1},{1,0},{1,1}},
    {{0,0},{0,1},{1,0},{1,1}},
    {{0,0},{0,1},{1,0},{1,1}}
};

int iRotations[4][4][2] = {
    {{1,0},{1,1},{1,2},{1,3}},
    {{0,1},{1,1},{2,1},{3,1}},
    {{2,0},{2,1},{2,2},{2,3}},
    {{0,2},{1,2},{2,2},{3,2}}
};

int lRotations[4][4][2] = {
    {{0,0},{0,1},{0,2},{1,2}},
    {{0,0},{1,0},{2,0},{0,1}},
    {{0,0},{1,0},{1,1},{1,2}},
    {{0,1},{1,1},{2,1},{2,0}},
};

int jRotations[4][4][2] = {
    {{1,0},{1,1},{1,2},{0,2}},
    {{0,0},{0,1},{1,1},{2,1}},
    {{0,0},{1,0},{0,1},{0,2}},
    {{0,0},{1,0},{2,0},{2,1}},
};

int tRotations[4][4][2] = {
    {{1,0},{0,1},{1,1},{2,1}},
    {{0,0},{0,1},{1,1},{0,2}},
    {{0,0},{1,0},{2,0},{1,1}},
    {{1,0},{0,1},{1,1},{1,2}},
};

int sRotations[4][4][2] = {
    {{0,1},{1,0},{1,1},{2,0}},
    {{0,0},{0,1},{1,1},{1,2}},
    {{0,1},{1,0},{1,1},{2,0}},
    {{0,0},{0,1},{1,1},{1,2}}
};

int zRotations[4][4][2] = {
    {{0,0},{1,0},{1,1},{2,1}},
    {{1,0},{0,1},{1,1},{0,2}},
    {{0,0},{1,0},{1,1},{2,1}},
    {{1,0},{0,1},{1,1},{0,2}}
};

int (*rotation[7])[4][2] = {
    lRotations,jRotations,tRotations,sRotations,zRotations,iRotations,oRotations
};

void tTypeColour(tType type, int *r, int *g, int *b) {
    switch (type) {
        case L:
            *r = 0;
            *g = 0;
            *b = 255;
            break;
        case J:
            *r = 225;
            *g = 100;
            *b = 0;
            break;
        case T:
            *r = 250;
            *g = 0;
            *b = 230;
            break;
        case S:
            *r = 255;
            *g = 0;
            *b = 0;
            break;
        case Z:
            *r = 0;
            *g = 255;
            *b = 0;
            break;
        case I:
            *r = 0;
            *g = 20;
            *b = 255;
            break;
        case O:
            *r = 0;
            *g = 150;
            *b = 30;
            break;
    }
};

tetromino newTetromino(tType type) {
    tetromino t;
    t.type = type;
    for (int i=0; i<4; i++) {
        t.blocks[i][0] = rotation[type][0][i][0];
        t.blocks[i][1] = rotation[type][0][i][1];
        // t.blocks[i][0] = PIECES[type].blocks[i][0];
        // t.blocks[i][1] = PIECES[type].blocks[i][1];
    }
    t.rotation = 0;
    return t;
}

// -1 means cant go left, 1 means cant go right, 0 means valid to move either
int canSlide(tetromino *t, Game *game, int dir) {
    int newPos[2];
    switch (dir) {
        case -1:
            //left test case
            newPos[0] = t->position[0] - 1;
            newPos[1] = t->position[1];
            for (int i=0; i<4; i++) {
                if (newPos[0]+t->blocks[i][0] < 0) {
                    return -1;
                }
                if (game->grid[newPos[0]+t->blocks[i][0]][newPos[1]+t->blocks[i][1]] == 1) {
                    return -1;
                }
            }
            return 0;
        case 1:
            //right test case
            newPos[0] = t->position[0] + 1;
            newPos[1] = t->position[1];
            for (int i=0; i<4; i++) {
                if (newPos[0]+t->blocks[i][0] > 9) {
                    return 1;
                }
                if (game->grid[newPos[0]+t->blocks[i][0]][newPos[1]+t->blocks[i][1]] == 1) {
                    return 1;
                }
            }
            return 0;
    }
}

int canFall(tetromino* t, Game *game) {
    int newPos[] = {t->position[0], t->position[1] + 1};
    for (int i = 0;i < 4; i++) {
        if (newPos[1]+t->blocks[i][1] >= 20) {
            return 0;
        }
        if (game->grid[newPos[0]+t->blocks[i][0]][newPos[1]+t->blocks[i][1]] == 1){
            return 0;
        }
    }
    return 1;
}

tetromino getGhost(tetromino* t, Game *game) {
    tetromino ghost = *t;
    while (canFall(&ghost, game) == 1) {
        ghost.position[1]++;
    }
    return ghost;
}

void lockTetromino(tetromino *t, Game *game) {
    // printf("Locking tetromino\n");
    tetromino ghost = getGhost(t, game);
    for (int i = 0;i < 4; i++) {
        game->grid[ghost.position[0]+ghost.blocks[i][0]][ghost.position[1]+ghost.blocks[i][1]] = 1;
        game->gridColours[ghost.position[0]+ghost.blocks[i][0]][ghost.position[1]+ghost.blocks[i][1]] = t->type;
    }
}

void nextBlock(tetromino *t) {
    tetromino nextBlock = newTetromino(rand() % 7);

    *t = nextBlock;
    t->position[0] = 4;
    t->position[1] = 0;
}

void rotate(tetromino *t, int direction) {
    //dir 1: rotate right
    //dir -1: rotate left
    // printf("rotating piece of type %d\n", t->type);
    t->rotation = (t->rotation + direction + 4) % 4;

    for (int i=0; i<4; i++) {
        t->blocks[i][0] = rotation[t->type][t->rotation][i][0];
        t->blocks[i][1] = rotation[t->type][t->rotation][i][1];
    }
}

int scores[4] = {
    100, 300, 500, 700
};

void checkGrid(Game *game) {
    int lineCount = 0;

    int y = 19;

    while (y > 0) {
        int full = 1;
        for (int x=0; x<10; x++) {
            if (game->grid[x][y] == 0) {
                full = 0;
                y--;
                break;
            }
        }
        if (!full) continue;
        lineCount++;
        for (int i=y; i>0; i--) {
            for (int x=0; x<10; x++) {
                game->grid[x][i] = game->grid[x][i-1];
                game->gridColours[x][i] = game->gridColours[x][i-1];
            }
        }
    }
    if (lineCount == 0) return;
    game->lineCount += lineCount;
    game->score += scores[lineCount-1];
}

void displayGrid(int g[10][20]) {
    for (int y=0; y<20; y++) {
        for (int x=0; x<10; x++) {
            printf("%d ", g[x][y]);
        }
        printf("\n");
    }
}

void storeBlock(tetromino *current, tetromino *storedBlock) {
    if (storedBlock->type == -1) {
        *storedBlock = *current;
        nextBlock(current);
    }else {
        tetromino temp = *storedBlock;
        *storedBlock = *current;
        *current = temp;
    }
    current->position[0] = 4;
    current->position[1] = 0;
    storedBlock->position[0] = 4;
    storedBlock->position[1] = 0;
}

void restart(tetromino *currentBlock, tetromino *storedBlock, Game *game) {
    for (int y=0; y<20; y++) {
        for (int x=0; x<10; x++) {
            game->grid[x][y] = 0;
            game->gridColours[x][y] = -1;
        }
    }

    storedBlock->type = -1;

    currentBlock->position[0] = 4;
    currentBlock->position[1] = 0;

    game->lineCount = 0;
    game->score = 0;
}

void updateText(SDL_Renderer *renderer, TTF_Font *font, SDL_Texture **texture, Game *g) {
    SDL_DestroyTexture(*texture);
    char text[64];
    sprintf(text, "Line Count: %d\n\nScore: %d", g->lineCount, g->score);
    SDL_Color color = {255, 255, 255, 255};
    SDL_Surface *surface = TTF_RenderUTF8_Blended_Wrapped(font, text, color, 3000);
    *texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_FreeSurface(surface);
}

int main(int argc, char *argv[]) {
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL_Init Error: %s\n", SDL_GetError());
        return 1;
    }
    SDL_Window *win = SDL_CreateWindow("Tetris", 100, 100, 650, 800, SDL_WINDOW_SHOWN);
    if (win == NULL) {
        printf("SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    TTF_Init();
    TTF_Font *font = TTF_OpenFont("/System/Library/Fonts/Monaco.ttf", 20);


    const Uint8 *state = SDL_GetKeyboardState(NULL);

    // int grid[10][20] = {0};

    tetromino lBlock = {{{0,0},{0,1}, {0,2}, {1,2}},{4,0}};
    tetromino jBlock = {{{1,0}, {1,1}, {1,2}, {0,2}}, {4,0}};
    tetromino oBlock = {{ {0,0},{0,1}, {1,0}, {1,1}}, {4,0}};
    tetromino tBlock = {{{0,1},{1,0},{1,1},{1,2}},{4,0}};
    tetromino iBlock = {{{0,0},{0,1},{0,2},{0,3}},{4,0}};
    tetromino sBlock = {{{1,0},{2,0},{0,1},{1,1}},{4,0}};
    tetromino zBlock = {{{0,0},{1,0},{1,1},{2,1}},{4,0}};

    tetromino currentBlock = sBlock;
    currentBlock.type = S;

    tetromino storedBlock;
    storedBlock.type = -1;

    Game game;
    game.lineCount = 0;
    game.score = 0;
    for (int y=0; y<20; y++) {
        for (int x=0; x<10; x++) {
            game.grid[x][y] = 0;
            game.gridColours[x][y] = -1;
        }
    }

    int lineCount = 0;

    SDL_Renderer *renderer = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);

    SDL_Color color = {255, 255, 255, 255};
    SDL_Surface *surface = TTF_RenderUTF8_Blended_Wrapped(font, "Line Count: 0\n\nScore: 0", color, 3000);
    SDL_Texture *textTexture = SDL_CreateTextureFromSurface(renderer, surface);

    SDL_Event e;
    int running = 1;
    int paused = 0;

    Uint32 lastDropTime = SDL_GetTicks();
    Uint32 lastHorizontalTime = lastDropTime;
    Uint32 lastHardDropTime = lastDropTime;
    Uint32 lastSoftDropTime = lastDropTime;

    while (running) {
        while (SDL_PollEvent(&e)) {
            switch(e.type) {
                case SDL_QUIT:
                    running = 0;
                    break;
                case SDL_KEYDOWN:
                    // printf("keydown!\n");
                    // printf("key pressed: %d, SDL_SCANCODE_SPACE is %d\n", e.key.keysym.scancode, SDL_SCANCODE_ESCAPE);
                    if (e.key.keysym.scancode == SDL_SCANCODE_ESCAPE) {
                        paused = !paused;
                    }
                    if (!paused) {
                        if (e.key.keysym.scancode == SDL_SCANCODE_E) {
                            rotate(&currentBlock, 1);
                        }
                        if (e.key.keysym.scancode == SDL_SCANCODE_Q) {
                            rotate(&currentBlock, -1);
                        }
                        if (e.key.keysym.scancode == SDL_SCANCODE_SPACE) {
                            storeBlock(&currentBlock, &storedBlock);
                        }
                        if (e.key.keysym.scancode == SDL_SCANCODE_R) {
                            restart(&currentBlock, &storedBlock, &game);
                            updateText(renderer, font, &textTexture, &game);
                        }
                    }
                    break;
            }
        }

        if (!paused) {
            //moving current block
            if (SDL_GetTicks() - lastDropTime > 500) {
                //tick for block to move
                if (canFall(&currentBlock, &game) == 1) {
                    currentBlock.position[1]++;
                    lastDropTime = SDL_GetTicks();
                }else {
                    lockTetromino(&currentBlock, &game);
                    // printf("%d\n", grid[currentBlock.position[0]][currentBlock.position[1]]);
                    nextBlock(&currentBlock);
                    checkGrid(&game);
                    updateText(renderer, font, &textTexture, &game);
                }
            }


            if (SDL_GetTicks() - lastHardDropTime > 500) {
                if (state[SDL_SCANCODE_UP]) {
                    lockTetromino(&currentBlock, &game);
                    nextBlock(&currentBlock);
                    checkGrid(&game);
                    updateText(renderer, font, &textTexture, &game);
                    lastHardDropTime = SDL_GetTicks();
                }
            }

            if (SDL_GetTicks() - lastSoftDropTime > 50) {
                if (state[SDL_SCANCODE_DOWN]) {
                    if (canFall(&currentBlock, &game) == 1) {
                        currentBlock.position[1]++;
                        lastSoftDropTime = SDL_GetTicks();
                    }
                    //should the last drop time be synced with soft drop(manual drop)???
                }
            }

            if (SDL_GetTicks() - lastHorizontalTime > 100) {
                if (state[SDL_SCANCODE_LEFT] && canSlide(&currentBlock, &game, -1) >= 0) {
                    currentBlock.position[0]--;
                    lastHorizontalTime = SDL_GetTicks();
                }
                if (state[SDL_SCANCODE_RIGHT] && canSlide(&currentBlock, &game, 1) <= 0) {
                    currentBlock.position[0]++;
                    lastHorizontalTime = SDL_GetTicks();
                }
            }

            //clears screen
            SDL_RenderClear(renderer);

            SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
            for (int x = 0; x < 10; x++) {
                for (int y = 0; y < 20; y++) {
                    SDL_Rect cell = {XOFFSET+(x*30), YOFFSET+(y*30), 30, 30};
                    if (game.grid[x][y] == 1) {
                        int r = 0;
                        int g = 0;
                        int b = 0;
                        tTypeColour(game.gridColours[x][y], &r, &g, &b);
                        SDL_SetRenderDrawColor(renderer, r, g, b, 255);
                        SDL_RenderFillRect(renderer, &cell);
                        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
                    }else if (game.grid[x][y] == 0) {
                        SDL_RenderDrawRect(renderer, &cell);
                    }
                }
            }

            //ghost current block
            tetromino ghostCurrent = getGhost(&currentBlock, &game);
            int ghostAnchorX = ghostCurrent.position[0];
            int ghostAnchorY = ghostCurrent.position[1];
            for (int i=0; i<4 ;i++) {
                int r,g,b;
                tTypeColour(currentBlock.type, &r, &g, &b);
                SDL_SetRenderDrawColor(renderer, r*0.8,g*0.8,b*0.8,120);
                SDL_Rect cell = {XOFFSET+(ghostAnchorX+ghostCurrent.blocks[i][0])*30,YOFFSET+(ghostAnchorY+ghostCurrent.blocks[i][1])*30,30,30};
                SDL_RenderFillRect(renderer, &cell);
                SDL_SetRenderDrawColor(renderer, 200, 200, 200, 255);
            }

            //current block
            int anchorX = currentBlock.position[0];
            int anchorY = currentBlock.position[1];
            for (int i=0; i<4; i++) {
                int r,g,b = 0;
                tTypeColour(currentBlock.type, &r, &g, &b);
                SDL_SetRenderDrawColor(renderer, r,g,b,255);
                SDL_Rect cell = {XOFFSET+((anchorX+currentBlock.blocks[i][0])*30), YOFFSET+((anchorY+currentBlock.blocks[i][1])*30), 30, 30};
                SDL_RenderFillRect(renderer, &cell);

            }
            SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);

            //stored block
            if (storedBlock.type != -1) {
                for (int i=0; i<4; i++) {
                    int r,g,b;
                    tTypeColour(storedBlock.type, &r, &g, &b);
                    SDL_SetRenderDrawColor(renderer, r,g,b,255);
                    SDL_Rect cell = {XOFFSET+ 320 + storedBlock.blocks[i][0]*30, YOFFSET+120+storedBlock.blocks[i][1]*30, 30, 30};
                    SDL_RenderFillRect(renderer, &cell);
                }
                SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
            }



            int w, h;
            SDL_QueryTexture(textTexture, NULL, NULL, &w, &h);
            SDL_Rect rect = {375, 160, w, h};
            SDL_RenderCopy(renderer, textTexture, NULL, &rect);

            // if (textTexture == NULL) {
            //     printf("Texture is NULL\n");
            // }
            //
            // if (font == NULL) {
            //     printf("TTF_OpenFont Error: %s\n", TTF_GetError());
            // }

            // SDL_SetRenderDrawColor(renderer, 200, 200, 200, 200);



            SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);

            SDL_RenderPresent(renderer);
            SDL_Delay(16);
        }
    }
    SDL_DestroyWindow(win);
    SDL_Quit();
    return 0;
}