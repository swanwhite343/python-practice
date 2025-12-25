import numpy as np
from numpy.typing import NDArray

def get_hermitian_part(mat: NDArray[np.complex128]) -> NDArray[np.complex128]:
    return 0.5*(mat + mat.conj().T)