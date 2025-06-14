#include <string.h>
#include <gc.h>

void* alloc(size_t size)
{
    GC_INIT();
    return GC_malloc(size);
}

char* _strcat(const char* str1, const char* str2)
{
    GC_INIT();

    if (!str1 || !str2)
        return NULL;

    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);

    size_t total_len = len1 + len2 + 1;

    char* result = (char*)GC_malloc(total_len);

    if (!result)
        return NULL;

    strcpy(result, str1);
    strcat(result, str2);

    return result;
}
