int cut_rectangle_in_half(const int side_A, const int side_B) {
	int a = side_A;
	int b = side_B;
    if (a == b) {
        return a * b;
    }
    
    int cuts_a = 0;
    while (a % 2 == 0) {
        a /= 2;
        cuts_a++;
    }
    
    int cuts_b = 0;
    while (b % 2 == 0) {
        b /= 2;
        cuts_b++;
    }
    
    return (1 << cuts_a) * (1 << cuts_b);
}