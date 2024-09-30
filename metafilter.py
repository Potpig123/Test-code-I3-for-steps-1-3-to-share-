import numpy as np


def metafilter(file_dir):
    raw_meta = np.loadtxt(file_dir, str, delimiter=',', usecols=(0,1,2,8),skiprows=1)
    print('Raw meta size:',raw_meta.shape)
    ## filter1
    ### filt out empty KLGlast score
    filter1 = ~(raw_meta == '').any(axis = 1)
    nonempty_meta = raw_meta[filter1]
    print('Non-empty meta size:',nonempty_meta.shape)
    np.savetxt('/xdisk/hongxuding/jinchengyu/OA/meta/nonempty_longknee.csv', nonempty_meta, 
               delimiter=',',fmt="%s")


    """
    ### filt out KLGlast score <= 2 
    KLGlast = nonempty_meta[:,3].astype(np.uint8)
    filter2 = KLGlast<=2
    le2_meta = nonempty_meta[filter2]
    print('Less or equal 2 meta size:', le2_meta.shape)

    np.savetxt('/xdisk/hongxuding/jinchengyu/OA/meta/filtered_longknee.csv', le2_meta, 
               delimiter=',',fmt="%s")
    """

def record_wise_le2(nonempty_file):
    f = np.loadtxt(nonempty_file, str, delimiter=',', usecols=(0,2,3))
    scores = f[:,2].astype(np.uint8)

    names_g2 = []
    names_le2 = []
    for idx in range(len(f)):
        if scores[idx] <= 2:
            names_le2.append(f[idx][0] + f[idx][1])
        else:
            names_g2.append(f[idx][0] + f[idx][1])
    names_g2 = np.array(names_g2)
    names_le2 = np.array(names_le2)
    intersection = np.intersect1d(names_le2,names_g2)
    print('Greater or equal 2 record size:',names_g2.shape)
    print('Less or equal 2 record size:',names_le2.shape)
    print('Intersected record size:',intersection.shape)
    le2_filter = ~np.isin(names_le2, intersection)
    le2_filtered_names = names_le2[le2_filter]
    print('Filtered le2 records size:', le2_filtered_names.shape)

    unique_le2 = np.unique(le2_filtered_names)
    lines = []
    for name in unique_le2:
        lines.append(name[:7])
        lines.append(name[7:])
    lines = np.array(lines).reshape(-1,2)
    np.savetxt('/xdisk/hongxuding/jinchengyu/OA/meta/filtered_le2_meta.csv', lines,
               delimiter=',',fmt='%s')
    

if __name__ == '__main__':
    file_dir = '/xdisk/hongxuding/jinchengyu/OA/meta/longknee.csv'
    nonempty_file = '/xdisk/hongxuding/jinchengyu/OA/meta/nonempty_longknee.csv'
#    metafilter(file_dir)
    record_wise_le2(nonempty_file)