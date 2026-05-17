int cut_rectangle_in_half(const int side_A, const int side_B)
{
	int current_side_A = side_A;
    int current_side_B = side_B;
    
	int rectangle_count_on_side_A = 1;
	while (current_side_A % 2 == 0)
    {
        current_side_A /= 2;
        rectangle_count_on_side_A *= 2;
    }
    
	int rectangle_count_on_side_B = 1;
	while (current_side_B % 2 == 0)
    {
        current_side_B /= 2;
        rectangle_count_on_side_B *= 2;
    }
    
	int rectangle_count = rectangle_count_on_side_A * rectangle_count_on_side_B;
    
	return rectangle_count;
}