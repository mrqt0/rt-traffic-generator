# rt-traffic-generator

The Real Time Traffic Generator and Analyzer!

## Precondition

- rt-traffic-generator can operate in a fallback and full fledged mode. To
	operate in full fledged the send and the receive host need exactly
	synchronized clocks. This required GPS mouses or PTP. Sender as well as
	receiver are not build upon exact clocks, but the anayzer applications are!
	Make sure to pass **--swear-time-sync** flag to the applications to indicate
	(swear) that sender and receiver hosts operated with synchronize slots.

	Tip: before measurements you SHOULD connect both sender and receiver directly
	and do local tests. You should see delays raised by network adapters, network
	stack delay and operating system scheduling imprecisions. Often these variation
	are not to prevent. But you should consider using a realtime operating system,
	tune your network adapter, use realtime scheduling policies, etc.

## Test Description - Template Files

```
	{
			'payload-size' : 20,

			'initial-waittime' : 0.1,

			'bursts-packets' : 2,
			'burst-intra-time' : 0.1,
			'burst-inter-time' : 5.0
	},
	{
			'payload-size' : 20,

			'initial-waittime' : 1,

			'bursts-packets' : 2,
			'burst-intra-time' : 0.1,
			'burst-inter-time' : 5.0
	},
	{
			'payload-size' : 20,

			'initial-waittime' : 1,

			'bursts-packets' : 2,
			'burst-intra-time' : 0.1,
			'burst-inter-time' : 5.0
	},
	{
			'payload-size' : 20,

			'initial-waittime' : 1,

			'bursts-packets' : 2,
			'burst-intra-time' : 0.1,
			'burst-inter-time' : 5.0
	},
	{
			'payload-size' : 20,

			'initial-waittime' : 0.1,

			'bursts-packets' : 2,
			'burst-intra-time' : 0.1,
			'burst-inter-time' : 5.0
	}
```

## Execting Tests

### Start Receiver

The receiver should be started at the beginning. The output (JSON) is redirected to the file `rx.trace`.
Here template 5-streams-10-byte-random.conf is used.

```
./rt-traffic-generator-rx.py -f templates/5-streams-10-byte-random.conf > rx.trace
```

## Start Transmitter:

Similar the output is saved in tx.trace

```
./rt-traffic-generator-tx.py -f templates/5-streams-10-byte-random.conf > tx.trace
```

## End Test and Analysis

To finish the tests the transmitter should be killed first. Later the receiver.

Both files should be copied/moved to one PC.

The data can now be analyzed with one of the shipped scripts:

```
./analyzers/stats.py --trace-rx rx.trace --trace-tx tx.trace
```

## Trace File Format

```
{"payload-size": 20, "seq-no": 0, "stream": 0, "tx-time": "2017-07-05 20:14:45.537594"}
{"payload-size": 20, "seq-no": 0, "stream": 4, "tx-time": "2017-07-05 20:14:45.538174"}
{"payload-size": 20, "seq-no": 1, "stream": 0, "tx-time": "2017-07-05 20:14:45.638999"}
{"payload-size": 20, "seq-no": 1, "stream": 4, "tx-time": "2017-07-05 20:14:45.639444"}
{"payload-size": 20, "seq-no": 0, "stream": 1, "tx-time": "2017-07-05 20:14:46.439398"}
{"payload-size": 20, "seq-no": 0, "stream": 2, "tx-time": "2017-07-05 20:14:46.439857"}
{"payload-size": 20, "seq-no": 0, "stream": 3, "tx-time": "2017-07-05 20:14:46.440248"}
{"payload-size": 20, "seq-no": 1, "stream": 1, "tx-time": "2017-07-05 20:14:46.541070"}
{"payload-size": 20, "seq-no": 1, "stream": 2, "tx-time": "2017-07-05 20:14:46.541513"}
{"payload-size": 20, "seq-no": 1, "stream": 3, "tx-time": "2017-07-05 20:14:46.541891"}
{"payload-size": 20, "seq-no": 2, "stream": 0, "tx-time": "2017-07-05 20:14:50.745462"}
{"payload-size": 20, "seq-no": 2, "stream": 4, "tx-time": "2017-07-05 20:14:50.745927"}
{"payload-size": 20, "seq-no": 3, "stream": 0, "tx-time": "2017-07-05 20:14:50.846804"}
{"payload-size": 20, "seq-no": 3, "stream": 4, "tx-time": "2017-07-05 20:14:50.847249"}
{"payload-size": 20, "seq-no": 2, "stream": 1, "tx-time": "2017-07-05 20:14:51.645220"}
{"payload-size": 20, "seq-no": 2, "stream": 2, "tx-time": "2017-07-05 20:14:51.645686"}
{"payload-size": 20, "seq-no": 2, "stream": 3, "tx-time": "2017-07-05 20:14:51.646116"}
{"payload-size": 20, "seq-no": 3, "stream": 1, "tx-time": "2017-07-05 20:14:51.746953"}
{"payload-size": 20, "seq-no": 3, "stream": 2, "tx-time": "2017-07-05 20:14:51.747402"}
{"payload-size": 20, "seq-no": 3, "stream": 3, "tx-time": "2017-07-05 20:14:51.747783"}
{"payload-size": 20, "seq-no": 4, "stream": 0, "tx-time": "2017-07-05 20:14:55.953203"}
[...]
```
