int cut_rectangle_in_half(const int side_A, const int side_B) {

	int count = 1;

	int copMax_size = side_A;
	int copMin_size = side_B;


	



	while (copMax_size != 1 && copMin_size != 1) 
		{

		if (max_size % 2 == 0 || min_size % 2 == 0) {

			if (copMax_size % 2 == 0) {
				copMax_size /= 2;
			}
			else {
				copMin_size /= 2;
			}

			if (copMax_size < copMin_size)
			{
				int x = 0;

				x = copMax_size;

				copMax_size = copMin_size;

				copMin_size = x;

			}

			count++;


		}


	}



	return count;

}
