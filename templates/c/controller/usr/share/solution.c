#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

int is_numeric(char c){
    return c>='0' && c<='9';
}
int is_possible_first_char(char c){
    return is_numeric(c) || c=='-' || c=='+';
}

int *get_randomized(const char *text_p, unsigned *db, int *sum){
    char *tmp;
    char  state;
    long  tmp_n;
    int  *data=NULL;
    int  *data_new=NULL;
    char *text=malloc(sizeof(char) * (strlen(text_p)+2) );
    char *text_i;
    int   i;
    unsigned   rnd1;
    unsigned   rnd2;
    FILE *rnd_src;


    *db = 0;
    *sum = 0;

    if(text == NULL)
        return NULL;

    memset(text, 0, strlen(text_p)+2);
    strcpy(text, text_p);

    text_i = text;
    if (is_possible_first_char(*text_i))
        state = 2;
    else
        state = 1;


    while(*text_i){
        // get to next possible number
        if (state == 1)
        {
            while( *text_i && !is_possible_first_char(*text_i) )
                text_i++;

            if(*text_i)
                state = 2;
        }

        if (state == 2)
        {
            tmp = text_i;
            text_i++;
            while( is_numeric(*text_i) )
                text_i++;
            *text_i='\x00';
            tmp_n = strtol(tmp, NULL, 10);

            if(tmp_n > INT_MAX || tmp_n < INT_MIN){
                state=1;
                text_i++;
                continue;
            }

            if( (*sum) + tmp_n > INT_MAX ||
                (*sum) + tmp_n < INT_MIN ){
                *db = 0;
                *sum = 0;
                free(data);
                free(text);
                return NULL;
            }
            (*sum) += tmp_n;
            (*db)++;
            if(data)
                data_new = realloc(data, (*db)*sizeof(int));
            else
                data_new = malloc(sizeof(int));

            if(data_new){
                data_new[*db-1] = tmp_n;
                data = data_new;
            }else{
                *db = 0;
                *sum = 0;
                free(data);
                free(text);
                return NULL;
            }
            state=1;
        }
        text_i++;
    }
    free(text);

    rnd_src = fopen("/dev/urandom", "rb");
    for (i = 0; i < *db; ++i){
        fread(&rnd1, 1, 4, rnd_src);
        fread(&rnd2, 1, 4, rnd_src);
        rnd1 %= (*db);
        rnd2 %= (*db);
        //printf("%d, %d\n", rnd1, rnd2);
        tmp_n = data[rnd1];
        data[rnd1] = data[rnd2];
        data[rnd2] = tmp_n;
    }
    fclose(rnd_src);

    return data;
}
