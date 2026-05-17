int cut_rectangle_in_half(const int side_A, const int side_B) {
	if (side_A == 1 && side_B == 1) {
		return 1;
	}
	int count = 1;
	int a = side_A;
	int b = side_B;
	while(a >= 1 && b >= 1){ 
		if (a % 2 ==0  && b % 2 !=0) {
			a /= 2;
		}
		else if(b % 2 == 0) {
			b /= 2;
		}
		else {
			break;
		}
		count *= 2;
	}
	return count;
}