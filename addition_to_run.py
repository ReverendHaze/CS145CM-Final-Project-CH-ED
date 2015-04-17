def get_histograms(city, n_days=0, n_hours=1, n_minutes=0):

    master_df = master_df.loc[(master_df['City']==city), 'text']

    t_step = datetime.timedelta(days=n_days, minutes=n_minutes, hours=n_hours)

    # create empty dictionary
    histograms = {}

    # loop over master_df by timestep
    t_start = master_df.DatetimeIndex.min()
    t_max = master_df.DatetimeIndex.max()

    while t_start <= t_max:
        t_end = t_start + t_step

        # get dictionary of bigrams and their frequency within the timestep
        freq_dict = Corey(master_df[master_df.index < t_end])

        # remove current timestep from master_df and update end of next timestep
        master_df = master_df[master_df.index >= t_start]
        t_start = t_end

        # add that timestep's output to main histogram dictionary
        for key, value in freq_dict.iteritems():
            if key in histograms:
                histograms[key] = histograms[key].append(value)
            else:
                histograms[key] = np.array([value])

    #return completed dictionary of histogram vectors
    return histograms
