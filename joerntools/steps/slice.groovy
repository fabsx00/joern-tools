Gremlin.defineStep('forwardSlice', [Vertex, Pipe], { symbols ->
	 MAX_LOOPS = 5;
  	_()
	.copySplit(
		_(),
		_().transform{
			it.sideEffect{first = true;}
			.outE('REACHES', 'CONTROLS')
			.filter{it.label == 'CONTROLS' || !first || it.var in symbols}
			.inV().gather{it}.scatter()
			.sideEffect{first = false}
			.loop(4){it.loops < MAX_LOOPS}{true}
		}.scatter()
	).fairMerge()
	.dedup()
});

Gremlin.defineStep('backwardSlice', [Vertex, Pipe], { symbols ->
	MAX_LOOPS = 5;
	_()
	.copySplit(
		_(),
		_().transform{
			it.sideEffect{first = true;}
			.inE('REACHES', 'CONTROLS')
			.filter{it.label == 'CONTROLS' || !first || it.var in symbols}
			.outV().gather{it}.scatter()
			.sideEffect{first = false}
			.loop(4){it.loops < MAX_LOOPS}{true}
		}.scatter()
	).fairMerge()
	.dedup()
});

/**
   Starting from an argument node, slice backwards, but for data flow,
   consider only the symbols actually used in the argument.
*/

Gremlin.defineStep('sliceBackFromArgument', [Vertex, Pipe], {
	_().transform{
		symbols = it.uses().code.toList();
		it.statements().backwardSlice(symbols)
	}.scatter()
})

/**
   Starting from an argument node, slice forward, but for data flow,
   consider only the symbols actually used in the argument.
*/

Gremlin.defineStep('sliceForwardFromArgument', [Vertex, Pipe], {
	_().transform{
		symbols = it.uses().code.toList();
		it.statements().forwardSlice(symbols)
	}.scatter()
})

/**
   Slice forward from assignment, but for data flow, consider only the
   symbols defined on the left-hand side of the assignment.
*/

Gremlin.defineStep('sliceForwardFromAssign', [Vertex, Pipe], {
	_()
	.transform
	{
      		callee = it.code;
      		symbols = it.lval().code.toList()
		it.statements().forwardSlice(symbols)
	}.scatter()
})