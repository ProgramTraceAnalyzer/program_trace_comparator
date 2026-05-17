int cut_rectangle_in_half(const int side_A, const int side_B)
{
    int count=1, st2a=2, st2b = 2;
    while ((side_A % st2a) == 0)
    {
        count *= 2;
        st2a *= 2;
    }
    while ((side_B % st2b) == 0)
    {
        count *= 2;
        st2b *= 2;
    }
    return count;
}