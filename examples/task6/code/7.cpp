int cut_rectangle_in_half(const int side_A, const int side_B)
{
    int side_a = side_A;
    int side_b = side_B;
    int count = 1;
    if (side_a == side_b)
    {
        count = side_a * side_a;
    }
    else {
        while (side_a > 1 && side_b > 1)
        {
            if (side_a % 2 == 0 && (side_a >= side_b || side_b != 0))
            {
                side_a /= 2;
                count *= 2;
            }
            else if (side_b % 2 == 0)
            {
                side_b /= 2;
                count *= 2;
            }
            else
            {
                break;
            }
        }
    }
    

    return count;
}