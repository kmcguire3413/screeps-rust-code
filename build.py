#!/bin/python
import subprocess
import os
import shutil

def modifyasm(fin, fout):
	ifd = open(fin, 'r')
	ofd = open(fout, 'w')

	lines = ifd.readlines()

	ifd.close()

	ofd.write('module.exports = (function(global, env, buffer) {\n')

	for x in xrange(1, len(lines)):
		ofd.write(lines[x])

	ofd.close()

def check_env():
	print '------ checking environment -------'
	def check(cmd, msg):
		success = True
		try:
			subprocess.check_call(cmd, shell=True)
		except subprocess.CalledProcessError as e:
			print msg
			success = False

		return success

	return check('emcc -v', 'Could not execute emcc (Emscripten).') and check('cargo --version', 'Could not execute cargo (Rust).')

def build(inp, outp, md):
	print '------ building ------'
	subprocess.check_call('cargo build%s --target asmjs-unknown-emscripten' % md, shell=True) # --emit llvm-ir --crate-type lib test.rs
	subprocess.call('emcc --separate-asm -v %s -s NO_EXIT_RUNTIME=1 --bind -s STACK_OVERFLOW_CHECK=0 -s EXPORTED_FUNCTIONS="[\'_game_tick\', \'___allocate\']" -s ONLY_MY_CODE=1 --separate-asm -s SWAPPABLE_ASM_MODULE=1 -O3' % inp, shell=True)

	try:
		os.mkdir('./output')
	except:
		pass

	modifyasm('./a.out.asm.js', './output/rust.asm.js')

	os.remove('./a.out.asm.js')
	os.remove('./a.out.js')
	#os.remove('./a.out.js.mem')

	shutil.copyfile('./rust.boot.js', './output/rust.boot.js')

def main(debug):
	if check_env() is False:
		return

	if debug:
		md = ''
		sdir = 'debug'
	else:
		md = ' --release'
		sdir = 'release'

	build('./target/asmjs-unknown-emscripten/%s/libscreeps_rust_code.rlib' % sdir, './rust', md)

main(False)