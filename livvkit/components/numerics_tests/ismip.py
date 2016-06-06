# Copyright (c) 2015, UT-BATTELLE, LLC
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Utilities to provide numerical verification for the ISMIP test cases
"""
def ismip(model_path, bench_path, config):
    """ 
    Verify ISMIP-HOM model data against ISMIP's datasets 
    
    Args:
        model_path: Absolute path to the model data set
        bench_path: Absolute path to the benchmark data set
        config: A dictionary containing configuration options

    Returns:
        A result of the differences between the model and benchmark
    """
    result = LIVVDict()
    # Python2 equivalent call: np.loadtxt -> np.loadfromtxt
    x, y, vx_u, vx_std, vx_min, vx_max, vy_u, vy_std, vy_min, vy_max = (
        np.loadtxt(bench_path, unpack=True, delimiter=',',
        skiprows=1, usecols=(0,1,2,3,4,5,6,7,8,9)))
    
    n_pts = int(np.sqrt(len(x)))
    vnorm_mean =  np.reshape(np.sqrt(np.add(np.power(vx_u,2), np.power(vy_u,2))),\
                             (n_pts,n_pts))
    vnorm_stdev = np.reshape(np.sqrt(np.add(np.power(vx_std,2), np.power(vy_std,2))),\
                             (n_pts,n_pts))
    vnorm_plus =  np.reshape(np.add(vnorm_mean, vnorm_stdev), (n_pts,n_pts))
    vnorm_minus = np.reshape(np.subtract(vnorm_mean, vnorm_stdev), (n_pts,n_pts))
    vnorm_max = np.reshape(np.sqrt(np.add(np.power(vx_max,2), np.power(vy_max,2))),\
                           (n_pts,n_pts))
    vnorm_min = np.reshape(np.sqrt(np.add(np.power(vx_min,2), np.power(vy_min,2))),\
                           (n_pts,n_pts))
 
    # Grab the model data
    dataset = Dataset(model_path,'r')
    uvel  = dataset.variables['uvel'][0,0,:,:]
    vvel  = dataset.variables['vvel'][0,0,:,:]
    shape = np.shape(uvel)
    vnorm = np.sqrt(np.add(np.power(uvel,2), np.power(vvel,2)))
    floor = np.subtract(vnorm_min[1:-1,1:-1],   vnorm)
    ciel  = np.subtract(vnorm_max[1:-1,1:-1],   vnorm)
    under = np.subtract(vnorm_minus[1:-1,1:-1], vnorm)
    over  = np.subtract(vnorm_plus[1:-1,1:-1],  vnorm)
    bad_data = np.zeros(shape)
    for i in range(shape[0]):
        for j in range(shape[0]):
            if floor[i,j]>0:
                bad_data[i,j] = -2 # CISM < MIN_ISMIP
            elif ciel[i,j]<0:
                bad_data[i,j] = 2  # CISM > MAX_ISMIP
            elif under[i,j]>0:
                bad_data[i,j] = -1 # CISM < MU - SIGMA 
            elif over[i,j]<0:
                bad_data[i,j] = 1  # CISM > MU + SIGMA
    mean_diff = 100.0*np.divide(np.subtract(vnorm_mean[1:-1,1:-1], vnorm),\
                                            vnorm_mean[1:-1,1:-1])
    result["Mean % Difference"] = np.nanmean(mean_diff)
    return result


def populate_metadata():
    """ Provide some top level information for the summary """
    metadata = {}
    metadata["Type"] = "Summary"
    metadata["Title"] = "Numerics"
    metadata["Headers"] = ["Test1", "Test2"]
    return metadata

